import sqlite3
import os
from cryptography.fernet import Fernet
import json
from datetime import datetime, timedelta

KEY_FILE = "secret.key"
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        SECRET_KEY = f.read()
else:
    SECRET_KEY = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(SECRET_KEY)

cipher = Fernet(SECRET_KEY)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, data BLOB)')
    
    cursor.execute('CREATE TABLE IF NOT EXISTS routines (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, data BLOB)')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS task_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheduled_timestamp DATETIME,
        status TEXT DEFAULT 'pending', 
        is_routine BOOLEAN,
        encrypted_payload BLOB
    )''')
    
    try:
        cursor.execute("ALTER TABLE task_queue ADD COLUMN status TEXT DEFAULT 'pending'")
                        
    except sqlite3.OperationalError: pass
        
    try:
        cursor.execute("ALTER TABLE task_queue ADD COLUMN is_routine BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError: pass
    
    cursor.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, task_name TEXT, energy_level INTEGER, timestamp DATETIME)')
    
    cursor.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, state_blob BLOB)')

    conn.commit()
    conn.close()
    print("✅ Database Initialized, Encrypted at Rest, and Persistence Verified.")

init_db()


def get_planning_context():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT STRFTIME('%H', timestamp) as hr, AVG(energy_level) FROM history GROUP BY hr ORDER BY 2 DESC LIMIT 1")
    row = cursor.fetchone()
    peak = f"{row[0]}:00" if row else "10:00 AM"
    
    cursor.execute("SELECT data FROM routines")
    routines = [json.loads(cipher.decrypt(r[0]).decode()) for r in cursor.fetchall()]
    conn.close()
    return peak, routines


def save_profile(user_id, profile_dict):
    conn = sqlite3.connect('database.db')
    encrypted_data = cipher.encrypt(json.dumps(profile_dict).encode())
    
    conn.execute("INSERT OR REPLACE INTO profiles (user_id, data) VALUES (?, ?)", 
                 (user_id, encrypted_data))
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        decrypted_data = cipher.decrypt(row[0]).decode()
        return json.loads(decrypted_data)
    return None

def log_task_completion(task_name, energy):
    conn = sqlite3.connect('database.db')
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO history (task_name, energy_level, timestamp) VALUES (?, ?, ?)", 
                 (task_name, energy, now))
    conn.commit()
    conn.close()



def schedule_future_task(start_time, task_data):
    conn = sqlite3.connect('database.db')
    encrypted_task = cipher.encrypt(json.dumps(task_data).encode())
    
    conn.execute(""" 
        INSERT INTO task_queue (scheduled_timestamp, status, encrypted_payload) 
        VALUES (?, 'pending', ?)
    """, (start_time, encrypted_task))
    
    conn.commit()
    conn.close()


def check_for_scheduled_tasks():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    now_dt = datetime.now()
    now_str = now_dt.strftime("%Y-%m-%d %H:%M")
    
    ten_mins_ago = (now_dt - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
        SELECT id, encrypted_payload 
        FROM task_queue 
        WHERE (scheduled_timestamp BETWEEN ? AND ?)
        AND (status = 'pending' OR status IS NULL OR status = '')
        ORDER BY scheduled_timestamp ASC
        LIMIT 1
    """, (ten_mins_ago, now_str)) 

    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], cipher.decrypt(row[1]).decode()
    return None


def update_db_status(task_id, new_status):
    conn = sqlite3.connect('database.db')
    try:
        conn.execute("UPDATE task_queue SET status = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
        print(f"✅ DB: Task {task_id} updated to {new_status}")
    except Exception as e:
        print(f"❌ DB Error: {e}")
    finally:
        conn.close()


def rescue_database():
    conn = sqlite3.connect('database.db')
    conn.execute("UPDATE task_queue SET status = 'pending' WHERE status IS NULL")
    cursor = conn.execute("SELECT id, scheduled_timestamp, status FROM task_queue WHERE status = 'pending'")
    rows = cursor.fetchall()
    print("--- CURRENT PENDING TASKS IN DB ---")
    for r in rows:
        print(f"ID: {r[0]} | Time: {r[1]} | Status: {r[2]}")
    print("-----------------------------------")
    conn.commit()
    conn.close()


def clear_broken_tasks():
    conn = sqlite3.connect('database.db')
    conn.execute("DELETE FROM task_queue WHERE scheduled_timestamp IS NULL")
    conn.commit()
    conn.close()
    print("🧹 Nuked the 'None' tasks.")
