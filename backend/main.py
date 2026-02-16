
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from arch import handle_event
from LLMs import Demon,base_user_prompt
from avision import photo_bytes_to_claim
from initstate import init_state
from db import get_profile,save_profile
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is the "Master Switch" for your DBs
    from db import init_db
    from game import init_gamification_db
    
    init_db()               # Creates profiles, tasks, etc.
    init_gamification_db()  # Creates the user_stats table
    print("✅ All Systems Nominal: Databases Initialized.")
    yield

app = FastAPI(title="The Smart Companion", lifespan=lifespan)
model = Demon()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class AgentEvent(BaseModel):
    session_id: str  
    event_type: str  
    payload: str     
    energy_level: int = 10

class OnboardingUpdate(BaseModel):
    session_id: str
    responses: Dict[str, bool] 

sessions: Dict[str, Any] = {}

DEFAULT_PFP = {
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



@app.get("/")
async def health_check():
    return {"status": "The Smart Companion", "active_sessions": len(sessions)}

@app.post("/event")
async def handle_agent_event(event: AgentEvent):
    if not event.session_id:
        return {"data": {"type": "idle", "text": ""}}
        
    if event.session_id not in sessions:
        new_state = init_state()
        
        saved_pfp = get_profile(event.session_id)
        
        if saved_pfp:
            print(f"🧬 Restoring profile for {event.session_id}")
            new_state['user_pfp'].update(saved_pfp)
        
        sessions[event.session_id] = new_state

    state = sessions[event.session_id]

    try:
        ui_response = handle_event(
            event={"type": event.event_type, "payload": event.payload},
            state=state,
            el=event.energy_level,
            model=model,
            base_user_prompt=base_user_prompt
        )

        if "xp_total" in ui_response:
            state["total_xp"] = ui_response["xp_total"]
            state["level"] = ui_response["level"]
            state["streak"] = ui_response["streak"]
        
        
        ui_response["xp_total"] = state.get("total_xp", 0)
        ui_response["level"] = state.get("level", 1)
        ui_response["streak"] = state.get("streak", 0)

        return {"data": ui_response}

    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return {"data": {"type": "chat", "text": "Smart Companion link unstable..."}}

@app.get("/onboarding/next-question")
async def get_onboarding_question(step: int = 0):
    questions = [
        "I am The Smart Companion. Do you struggle with starting tasks?", 
        "Do you often find yourself losing track of time?",             # Step 1
        "Do large projects feel overwhelming without micro-steps?",      # Step 2
    ]
    
    if step < len(questions):
        return {
            "text": questions[step],
            "actions": [{"label": "YES", "payload": "YES"}, {"label": "NO", "payload": "NO"}],
            "next_step": step + 1 #
        }
    
    return {
        "text": "Sync complete! I am now tuned to your frequency.",
        "type": "complete",
        "next_step": 0 
    }

@app.post("/vision/{session_id}")
async def vision_analysis(session_id: str, file: UploadFile = File(...)):
    """
    Receives image, calls teammate's logic, and updates the ADHD State Machine.
    """
    if session_id not in sessions:
        sessions[session_id] = init_state()
    
    try:
        contents = await file.read()
        
        vision_claim = photo_bytes_to_claim(contents) 
        
        ui_response = handle_event(
            event={
                "type": "USER_INPUT", 
                "payload": f"[VISUAL_CONTEXT_SYNC]: {vision_claim}"
            },
            state=sessions[session_id],
            el=10, 
            model=model,
            base_user_prompt=base_user_prompt
        )
        
        return {
            "status": "vision_synced",
            "claim": vision_claim,
            "data": ui_response
        }
    except Exception as e:
        print(f"Vision Integration Error: {e}")
        raise HTTPException(status_code=500, detail="Vision pipeline failed")
class OnboardingUpdate(BaseModel):
    session_id: str
    responses: Dict[str, Any] 

@app.post("/onboarding/calibrate")
async def calibrate_profile(update: OnboardingUpdate):
    if update.session_id not in sessions:
        sessions[update.session_id] = init_state()
    
    state = sessions[update.session_id]
    
    state['user_pfp'].update(update.responses)
            
    try:
        save_profile(update.session_id, state['user_pfp'])
    except Exception as e:
        print(f"❌ DB Sync Failed: {e}")
            
    return {"message": "Success", "new_pfp": state['user_pfp']}

@app.post("/vision")
async def vision_pipeline(session_id: str, file: UploadFile = File(...)):
    """The friend's hook for image analysis."""
    if session_id not in sessions:
        sessions[session_id] = init_state()
    
    vision_description = "A messy kitchen with dirty dishes." 

    ui_response = handle_event(
        event={"type": "USER_INPUT", "payload": f"I see: {vision_description}"},
        state=sessions[session_id],
        el=10,
        model=model,
        base_user_prompt=base_user_prompt

    )
    
    return {"vision_result": vision_description, "agent_response": ui_response}

@app.post("/reset")
async def reset_session(session_id: str):
    """Wipes a specific session for testing."""
    if session_id in sessions:
        del sessions[session_id]
    return {"message": f"Session {session_id} wiped."}


@app.get("/heartbeat/{session_id}")
async def heartbeat(session_id: str):
    if session_id not in sessions: return {"type": "idle"}
    state = sessions[session_id]
    
    if state.get('active_steps') and state.get('last_action_timestamp'):
        import time
        idle_time = time.time() - state['last_action_timestamp']
        if idle_time > 300: # 5 minutes of silence
            return {
                "type": "nudge",
                "text": "Still working on that step, or are we stuck?",
                "options": ["Still on it", "Help!", "Skip"]
            }
    return {"type": "idle"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
