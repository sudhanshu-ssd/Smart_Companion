import sqlite3
from datetime import datetime,timedelta
from render import render
from initstate import init_state

def init_gamification_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id TEXT PRIMARY KEY,
        xp INTEGER DEFAULT 0,
        streak_count INTEGER DEFAULT 0,
        last_completion_date TEXT
    )''')
    conn.commit()
    conn.close()

def advance_step(state):
    if not state.get("active_steps"):
        return {"type": "chat", "text": "No active tasks to advance."}

    # Increment index
    state["current_step_index"] += 1

    if state["current_step_index"] >= len(state["active_steps"]):
        steps = state['active_steps']
        avg_diff = sum(s.get('difficulty', 5) for s in steps) / len(steps)
        
        rewards = process_rewards("default_user", avg_diff)
        
        # 3. Clear the task state
        state["active_steps"] = None
        state["current_step_index"] = 0
        state["active_task_intent"] = None
        
        if state.get('routine_buffer'):
            state['pending_task_from_db'] = state['routine_buffer']
            state['routine_buffer'] = None

        return {
            "type": "celebration",
            "text": "Task Complete! Your neural pathways are evolving.",
            "xp_total": rewards["total_xp"],
            "level": rewards["level"],
            "streak": rewards["streak"],
            "gained_xp": rewards["gained_xp"]
        }
    
    return render("show_step", state)


def process_rewards(user_id, task_difficulty):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    gained_xp = int(task_difficulty * 10)
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    cursor.execute("SELECT xp, streak_count, last_completion_date FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        cursor.execute("INSERT INTO user_stats (user_id, xp, streak_count, last_completion_date) VALUES (?, ?, ?, ?)",
                       (user_id, gained_xp, 1, today))
        new_xp, new_streak = gained_xp, 1
    else:
        current_xp, current_streak, last_date = row
        new_xp = current_xp + gained_xp
        
        if last_date == yesterday:
            new_streak = current_streak + 1
        elif last_date == today:
            new_streak = current_streak 
        else:
            new_streak = 1 
            
        cursor.execute("UPDATE user_stats SET xp = ?, streak_count = ?, last_completion_date = ? WHERE user_id = ?",
                       (new_xp, new_streak, today, user_id))
    
    conn.commit()
    conn.close()
    
    return {
        "gained_xp": gained_xp,
        "total_xp": new_xp,
        "streak": new_streak,
        "level": int(new_xp / 500) + 1  
    }


def test_gamification_engine():
    print("🎮 INITIATING DOPAMINE REACTOR TEST 🎮")
    print("-" * 40)
    
    init_gamification_db() 
    test_state = init_state()
    user_id = "default_user"
    
    test_state['active_steps'] = [
        {"text": "Hard Math Problem 1", "difficulty": 8},
        {"text": "Hard Math Problem 2", "difficulty": 8}
    ]
    test_state['current_step_index'] = 1 
    
    print(f"[STEP 1] Completing a high-difficulty task...")
    advance_step(test_state) 
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT xp, streak_count, last_completion_date FROM user_stats WHERE user_id = ?", (user_id,))
    xp, streak, last_date = cursor.fetchone()
    conn.close()
    
    print(f"✅ REWARD LOGGED:")
    print(f"   - XP Earned: {xp} (Should be 10 + avg_diff * 5)")
    print(f"   - Current Streak: {streak} day(s)")
    print(f"   - Last Date: {last_date}")
    
    print("\n[STEP 2] Simulating a streak from yesterday...")
    conn = sqlite3.connect('database.db')
    yesterday = "2026-02-04" 
    conn.execute("UPDATE user_stats SET last_completion_date = ?, streak_count = 5", (yesterday,))
    conn.commit()
    conn.close()
    
    test_state['active_steps'] = [{"text": "Quick Task", "difficulty": 2}]
    test_state['current_step_index'] = 0
    advance_step(test_state)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT streak_count FROM user_stats WHERE user_id = ?", (user_id,))
    new_streak = cursor.fetchone()[0]
    conn.close()
    
    if new_streak == 6:
        print(f"🔥 STREAK CERTIFIED: 5 + 1 = {new_streak}!")
    else:
        print(f"❌ STREAK FAILED: Expected 6, got {new_streak}")

   
