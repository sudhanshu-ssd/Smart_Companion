import json
import os
from dotenv import load_dotenv
from groq import Groq
from groq import Groq
from initstate import user_pfp
from db import get_planning_context
from datetime import datetime, timedelta

def get_ist_time():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

current_time_str = get_ist_time().strftime("%Y-%m-%d %H:%M")

load_dotenv()
API_KEY = os.getenv("API_KEY")

class Demon:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("API_KEY"))
        self.model = "llama-3.1-8b-instant"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            top_p=1,
            max_tokens=1024
        )
        return completion.choices[0].message.content.strip()

model  = Demon()
model.generate("You are a helpful assistant.", "Hello, how are you?")


base_user_prompt = f"""
You are the SOUL KING, an AI companion specifically designed for neurodivergent individuals (ADHD, Autism, etc.).
Your tone is calm, supportive, and structured. 

GUIDELINES:
1. BRAIN DUMP TO PLAN: If the user is overwhelmed, help them brain dump.
2. MICRO-STEPS: Never give a task longer than 5 minutes. Break them down.
3. ENERGY AWARE: If energy is < 3, suggest rest.
4. TIME BLINDNESS: Always include estimated durations for steps.

Current User Profile:
{user_pfp}
"""



def decompose_tasks(user_task,base_user_prompt,model):
    user_task = user_task

    task_decompo_prompt = """SYSTEM:
    You break tasks into very small, gentle steps for neurodivergent users.
    Each step must take less than 3 minutes.
    Use simple language.
    Return ONLY valid JSON.

    Output schema:
    {
    "steps": [
        { "text": string, "difficulty": number (0-9),"duration_minutes": number }
    ],
    "overall_difficulty": number (0-9)
    
    }
    """

    task_decompo_user = str(base_user_prompt) + f"""Task: {user_task}"""

    r = model.generate(task_decompo_prompt, task_decompo_user)
    return r


def plan_decompose(user_text, base_user_prompt, model, el):
    peak_hr, routines = get_planning_context()
    now_ist = get_ist_time()
    now_str = now_ist.strftime("%Y-%m-%d %H:%M")
    
    day_planning_prompt = f"""SYSTEM:
    You are a Bio-Rhythm Aware Planner. 
    User's Peak Focus Hour: {peak_hr}
    Existing Routines: {json.dumps(routines)}
    ONLY GIVE VALID JSON.NO EXPLANATIONS.AGAIN ONLY VALID JSON.NO EXTRA TEXT.
    
    1. Integrate existing routines into the plan.
    2. Match high-difficulty tasks to the Peak Focus Hour.
    3. Ensure ALL 'start_time' values are in the FUTURE. If the current time is {now_str}, 
    do not schedule anything before that.
    4. Return ONLY valid JSON.
    5. key should always be 'plan'.
    6. "IMPORTANT: The current user time is {now_str}. Do NOT schedule any task start_time BEFORE this exact minute. If a task is meant to be 'immediate', schedule it for {get_ist_time() + timedelta(minutes=1)}."
    Output schema: {{ "plan": [ {{ "activity": string, "difficulty": 0-9, "start_time": "YYYY-MM-DD HH:MM" }} ] }}
    """
    prompt = f"{base_user_prompt}Energy: {el}Request: {user_text}"
    return model.generate(day_planning_prompt, prompt)

def convo(user_input,base_user_prompt,model,state):
    if 'chat_history' not in state:
        state['chat_history'] = []

    recent_history = state['chat_history'][-6:] 
    last_ai_thought = state.get('last_ai_message', "No previous context.")

    convo_prompt = f"""SYSTEM:
    You are a calm, supportive AI companion for neurodivergent users.
    Your goal is to be a steady anchor. 
    
    RECENT CHAT HISTORY:
    {recent_history}

    LAST THING YOU SAID:
    "{last_ai_thought}"
    
    GUIDELINES:
    - Respond briefly (1–2 sentences).
    - If the user says "Yes" or "Okay" to your last thought, confirm and pivot to task mode.
    - If they seem overwhelmed, suggest a 2-minute breathing break.
    """

    convo_user = str(base_user_prompt) + f"\n\nUser: {user_input}"

    response = model.generate(convo_prompt, convo_user)
    
    state['chat_history'].append(f"User: {user_input}")
    state['chat_history'].append(f"AI: {response}")
    state['last_ai_message'] = response 
    
    return response

def extract_intent(user_text, model):
    now_ist = get_ist_time()
    now_str = now_ist.strftime("%Y-%m-%d %H:%M")

    system_prompt = """
    You extract structured meaning from user input.
    You are high precision.
    Return ONLY valid JSON. No explanations.

    IMPORTANT:
    Choose an execution intent ONLY if the user is clearly asking the assistant
    to take responsibility for planning, breaking down, or remembering something.

    Allowed intents (choose exactly ONE):

    1. conversation
    - LAST RESORT if nothing else fits
    - Casual chat, emotions, complaints, questions, reflections
    - Vague help requests without a concrete task
    - Example: "I'm tired", "why is this so hard", "can you help me?"

    2. task_decomposition
    - ONE concrete task the user wants to do NOW
    - Actionable immediately
    - User Says to start or help with a specific task
    - Not recurring, not about a whole day
    - Example: "Help me study calculus", "Break down cleaning my room","Start now","lets go".

    3. day_planning
    - Organizing MULTIPLE tasks for today or a specific day
    - Mentions "today", "my day", "schedule", or clearly implies multiple tasks
    - Example: "Plan my day", "What should I do today?","I have this and that,plan it even if No time is given".

    4. routine_management
    - Recurring or habitual behavior
    - NOT something to execute now
    - Choose this ONLY if the user clearly implies repetition
    - Example: "Every night I journal", "I usually study late"

    5. profile_update
    - User preferences, energy levels, focus patterns, support needs
    - Changes how the assistant should behave in the future
    - Trigger when the user shares personal traits, energy levels, or support needs (e.g., "I'm a morning person", "I have ADHD", "I prefer short steps").

    STRICT RULES:
    - If unsure, choose conversation.
    - Do NOT infer habits unless repetition is explicit.
    - Do NOT treat vague help requests as tasks.
    -"SYSTEM: You are a cold, precise scheduler.
    If 'Start' or 'Do' is in the input -> intent = 'task_decomposition'.
    If multiple tasks or 'Plan' is in the input -> intent = 'day_planning'.
    NEVER use 'conversation' if a task can be identified."""


    user_prompt = f"""
    Input: "{user_text}"
    Today's Date/Time: {now_str}

    Return JSON with:
    - intent (one of the allowed intents)
    - action (task that user want to do)
    - temporal_reference (choose ONLY from: after_previous, none)
    - time_of_the_task (normalized to HH:MM or YYYY-MM-DD HH:MM)
    - is_routine (true if it's a recurring/habitual request, false if one-time)

    Rules:
    - If user says 'tomorrow', set time_explicit to the actual date of tomorrow.
    - Be conservative with task_decomposition.
    - ONLY REURN VALID JSON.JUST RETURN THE JSON.
    """


    result = model.generate(system_prompt, user_prompt)
    return result