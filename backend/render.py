import json

def render(decision, state):
    if decision == "ask_commitment":
        task_id, payload = state['pending_task_from_db']
        task_info = json.loads(payload)
        return {
            "type": "commitment_check",
            "text": f"It's time for **{task_info['activity']}**. Ready?",
            "actions": [
                {"label": "I'M READY", "payload": "COMMIT_TASK"}, 
                {"label": "NOT NOW", "payload": "SKIP_TASK"}
            ]
        }
    
    if decision == "show_step":
        step = state['active_steps'][state['current_step_index']]
        return {
            "type": "step",
            "text": step['text'],
            "progress": f"{state['current_step_index'] + 1}/{len(state['active_steps'])}"
        }
        
    if decision == "suggest_break":
        return {"type": "break", "text": "Your energy is low. How about a 5-min breather?"}
        
    if decision == "IDLE":
        return {"type": "message", "text": "I'm here whenever you're ready."}
    
    if decision == "RESUME_PROMPT":
        task_name = state['paused_task'].get('activity', 'your previous task')
        return {
            "type": "chat", 
            "text": f"I noticed we paused on '{task_name}'. Ready to jump back in?",
            "actions": [{"label": "YES", "payload": "RESUME"}, {"label": "NO", "payload": "CANCEL_RESUME"}]
        }
    
    if decision == "SHOW_CHAT":
        msg = state["convo"]

        state["convo"] = None

        return {
            "type": "chat",
            "text": msg
        }

    if decision == "notify_routine_available":
        task_id, payload = state['routine_buffer']
        routine_name = json.loads(payload).get('activity', 'Routine')
        return {
            "type": "nudge",
            "text": f"🔔 Your routine '{routine_name}' is ready. Want to switch, or finish what you're doing?",
            "options": ["Switch to Routine", "Dismiss for now"]
        }
    
    if decision == "show_completion_celebration":
        r = state.get('last_reward', {})
        return {
            "type": "celebration",
            "text": f"🎉 Task Complete! You earned {r.get('gained_xp')} XP.",
            "subtext": f"Current Streak: {r.get('streak')} days!",
            "xp_total": r.get('total_xp')
        }

    fallback_text = state.get('convo') or "I'm here. What's the plan?"
    return {"type": "chat", "text": fallback_text}