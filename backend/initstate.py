def init_state():
    return {
        "current_intent": None,
        "active_task_intent": None,
        "active_plan": None,
        "plan_index": None,
        "active_steps": None,
        "current_step_index": 0,
        "paused_task": None,
        "paused": False,
        "onboarding_complete": False, 
        "onboarding_step": 0,
        "chat_history": [],
        "user_pfp": {
            "prefers_short_steps": True, 
            "time_blindness": True,
            "easily_overwhelmed": True,
            "prefers_voice": True
        },
        "total_xp": 0,
        "level": 1,
        "streak": 0,
        "focus_shields": 3
    }

user_pfp = {
  "prefers_short_steps": True,
  "needs_breaks": True,
  "time_blindness": True,
  "reading_difficulty": True,

  "easily_overwhelmed": True,
  "difficulty_starting_tasks": True,
  "loses_focus_easily": True,

  "prefers_voice": True,
  "needs_encouragement": True,

  "sensitive_to_pressure": True,
  "anxiety_with_tasks": True
}