import re
import json
from cryptography.fernet import Fernet
from datetime import datetime,timedelta
from game import advance_step
from LLMs import decompose_tasks, plan_decompose,convo,extract_intent
from render import render
from db import check_for_scheduled_tasks, update_db_status, schedule_future_task,save_profile
from initstate import user_pfp


def main_turn(user_text, state, user_pfp, el, model, base_user_prompt):
    if user_text:
        user_text = surgical_pii_masker(user_text)
        slots = json.loads(extract_intent(user_text, model))
        context_state_update(state, slots)

    decision = scheduler(user_pfp, el, state)
    
    ui_states = ["show_step", "suggest_break", "RESUME_PROMPT", "IDLE", 
                 "SHOW_CHAT", "ask_commitment", "notify_routine_available", 
                 "show_completion_celebration"]
    
    if decision in ui_states:
        return render(decision, state)

    executor(decision, user_text, state, base_user_prompt, model, el, user_pfp)
    
    
    state['current_intent'] = None
    
    new_decision = scheduler(user_pfp, el, state)
    return render(new_decision, state)


def scheduler(user_pfp, el, state):
    
    if state.get('convo'):
        return "SHOW_CHAT"

    if state.get('current_intent') in ["task_decomposition", "day_planning", "routine_management"]:
        if not state.get('active_steps') or state['current_intent'] == "routine_management":
            if state['current_intent'] == "day_planning": 
                return "plan_decompose"
            if state['current_intent'] == "routine_management": 
                return "routine_management"
            return "decompose_task"

    if state.get('current_intent') == "conversation":
        if state.get('active_steps'): 
            return "interruption"
        return "CHAT"

    if state.get('active_steps') and el <= 2:
        return "suggest_break"
    

    db_result = check_for_scheduled_tasks()
    if db_result is not None:  
        task_id, payload = db_result 
        task_data = json.loads(payload)
        
        if state.get('active_steps'):
            if task_data.get('is_routine'):
                if not (state.get('routine_buffer') and state['routine_buffer'][0] == task_id):
                    state['routine_buffer'] = (task_id, payload)
                    return "notify_routine_available"
        
        if not state.get('active_steps') and not state.get('pending_task_from_db'):
            state['pending_task_from_db'] = (task_id, payload)
            return "ask_commitment"
        
        if state.get('user_confirmed_commitment'):
            return "trigger_deferred_task"
        
    
   
    if state.get('paused_task') and not state.get('active_steps') and state.get('paused') is True:        
        return "RESUME_PROMPT"

    if state.get('active_steps'):
        return "show_step"

    return "IDLE"



def handle_event(event, state, el, model,base_user_prompt):

    if event["type"] == "USER_INPUT" and (event["payload"] == "HEARTBEAT" or event["payload"] == ""):
        return main_turn(
            user_text=None, 
            state=state,
            user_pfp=user_pfp,
            el=el,
            model=model,
            base_user_prompt=base_user_prompt
        )
    if event["type"] == "USER_INPUT":
        # Extract intent first to see if we are switching gears
        new_intent_data = extract_intent(event["payload"],model) 
        new_intent_data = json.loads(new_intent_data)
        
        # If the user is starting a NEW task, we must kill the old 'active_steps'
        if (new_intent_data['intent'] in ["task_decomposition", "day_planning"]and not state.get('paused_task')):

            if state.get('active_steps'):
                print("🧹 Cleaning up old task ghost...")
                state['active_steps'] = None
                state['current_step_index'] = 0
                state['active_task_intent'] = None
        
        state['current_intent'] = new_intent_data['intent']
        return main_turn(
            user_text=event["payload"],
            state=state,
            user_pfp=user_pfp,
            el=el,
            model=model,
            base_user_prompt=base_user_prompt
        )

    if event["type"] == "USER_ACTION":
        payload = event["payload"]
        
        if payload == "DONE":
            result = advance_step(state)
        
       
            if isinstance(result, dict) and result.get("type") == "celebration":
                return result
        
            return main_turn(None, state, None, el, model, base_user_prompt)
        elif payload == "RESUME":
            resume_task(state)
        elif payload == "CANCEL_RESUME":
            state['paused_task'] = None  
            
            state['paused'] = False 
            state['current_intent'] = "conversation"
            
            if state.get('pending_task_from_db'):
                update_db_status(state['pending_task_from_db'][0], "skipped")
                state['pending_task_from_db'] = None
                
            state['convo'] = "Everything cleared. I'm standing by for a fresh start."
            return main_turn(None, state, None, el, model, base_user_prompt)
        
        elif payload == "CANCEL_RESUME":
            state['paused_task'] = None  
            state['active_steps'] = None
            state['current_step_index'] = 0
            state['paused'] = False 
            state['current_intent'] = "conversation"
            
            if state.get('pending_task_from_db'):
                update_db_status(state['pending_task_from_db'][0], "skipped")
                state['pending_task_from_db'] = None
                
            state['convo'] = "Everything cleared. I'm standing by for a fresh start."
            return main_turn(None, state, None, el, model, base_user_prompt)
            
        elif payload == "COMMIT_TASK":
            state['user_confirmed_commitment'] = True
        elif payload == "SKIP_TASK":
            if state.get('pending_task_from_db'):
                update_db_status(state['pending_task_from_db'][0], "skipped")
                state['pending_task_from_db'] = None
        
        return main_turn(None, state, None, el, model, base_user_prompt)
    
    if event["type"] == "PROFILE_UPDATE":
        new_stats = event["payload"] 
        state['user_pfp'].update(new_stats)
        

        tuned_prompt = f"{base_user_prompt}\n\nUSER_CONSTRAINTS: {json.dumps(state['user_pfp'])}"
        
        state['convo'] = "Neural frequency tuned. I've adjusted my pacing to match your energy."
        
        return {
            "type": "chat", 
            "text": state['convo'],
            "onboarding_complete": True 
        }
    
def executor(decision, user_text, state, base_user_prompt, model, el, user_pfp):
    if decision == "decompose_task":
        res = decompose_tasks(user_text, base_user_prompt, model)
        state['active_steps'] = json.loads(res)["steps"]
        state['current_step_index'] = 0
        state['active_task_intent'] = "task_decomposition"

    elif decision == "trigger_deferred_task":
        task_id, payload = state['pending_task_from_db']
        state['pending_task_from_db'] = None
        
        task_info = json.loads(payload)
        
        update_db_status(task_id, "active")
        
        res = decompose_tasks(task_info['activity'], base_user_prompt, model)
        state['active_steps'] = json.loads(res)["steps"]
        state['current_step_index'] = 0
        
        
        state['user_confirmed_commitment'] = False

    elif decision == "interruption":
        pause_task(state)
        state['convo'] = convo(user_text, base_user_prompt, model,state)

    elif decision == "CHAT":
        state['convo'] = convo(user_text, base_user_prompt, model,state)
        
    if decision == "plan_decompose":
        res = plan_decompose(user_text, base_user_prompt, model, el)
        plan_data = json.loads(res)
        
        for item in plan_data['plan']:
            print(f"task-->{item}")
            schedule_future_task(item['start_time'], {
                "activity": item['activity'], 
                "difficulty": item.get('difficulty', 3),
                "origin": "day_planning"
            })
            
        state['convo'] = "I've organized your day around your energy peaks. I'll nudge you when it's time for each task!"
        state['current_intent'] = "conversation"
        state['active_plan'] = None 

    elif decision == "routine_management":
        slots = json.loads(extract_intent(user_text, model))
        act = slots.get('action') or slots.get('activity') or "New Routine"
        
        time_val = slots.get('time_of_the_task')
        if time_val and len(time_val) <= 5: 
            time_val = f"{datetime.now().strftime('%Y-%m-%d')} {time_val}"
            
        schedule_future_task(time_val, {
            "activity": act, 
            "is_routine": True,
            "difficulty": 3
        })
        
        state['convo'] = f"Locked in: {act} for {slots.get('time_of_the_task')}."
        state['current_intent'] = "conversation"

    

def surgical_pii_masker(text):
    if not isinstance(text, str):
        return text
    
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', text)
    
    text = re.sub(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE]', text)
    
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP_ADDR]', text)
    
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[ID_NUM]', text)
    
    return text


def context_state_update(state, slots):
    new_intent = slots.get("intent")
    state["current_intent"] = new_intent
    
    
    working_intents = ["day_planning", "task_decomposition", "routine_management"]
    if new_intent in working_intents:
        state["active_task_intent"] = new_intent




def pause_task(state):
    if state.get("active_steps"):
        state["paused_task"] = {
            "steps": state["active_steps"],
            "step_index": state["current_step_index"], 
            "intent": state["active_task_intent"], 
            "origin_text": state.get("last_user_text")
        }
        state["active_steps"] = None
        state["current_step_index"] = 0 
        state["paused"] = True

def interruption_handler(state):
    state['paused_task'] = {
        'steps': state['active_steps'],
        'step_index': state['current_step_index'], 
        'intent': state['active_task_intent']
    }
    state['active_steps'] = None 
    state['paused'] = True
    return "Task paused. I'm listening!"

def resume_task(state):
    if state.get('paused_task'):
        p = state['paused_task']
        state['active_steps'] = p['steps']
        state['current_step_index'] = p['step_index'] 
        state['active_task_intent'] = p['intent']
        
        state['paused_task'] = None
        state['paused'] = False
        state['current_intent'] = None 
        print("🔄 Task Resumed Successfully")

    

def clear_execution(state):
    state["active_steps"] = None
    state["current_step_index"] = None
    state['pause_task'] = None






