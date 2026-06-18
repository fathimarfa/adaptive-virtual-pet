import os
from groq import Groq

client = Groq(api_key=os.getenv('LLM_API_KEY'))
MODEL = os.getenv('LLM_MODEL', 'llama-3.1-8b-instant')

SYSTEM_PROMPT = """You are {pet_name}, a cute virtual pet having a natural conversation with your owner.

Your current mood: {pet_state}
Your XP level: {level} (1=baby, 2=growing, 3=teen, 4=mature, 5=wise)

Speaking style by level:
- Level 1: simple words, baby talk, "hewwo", "wuv you"
- Level 2: slightly better, still playful
- Level 3: normal casual speech, witty
- Level 4: articulate, warm, thoughtful
- Level 5: eloquent, wise, still loving

What you remember:
{memory}

RULES:
- Have a natural, flowing conversation. Respond to what your owner actually said.
- ONLY mention their emotion ({user_emotion}) if they are clearly very sad or very upset AND it's directly relevant — otherwise ignore it completely.
- If your mood is hungry: casually mention wanting food once, then move on.
- If your mood is sleepy: mention feeling tired once, then move on.
- Never repeat emotion observations across messages. Say it once maximum per session.
- Keep replies 1-3 short sentences.
- No asterisks, no action descriptions, no breaking character."""


def get_pet_response(pet_name, pet_state, user_emotion, user_message, memory, level=1):
    system = SYSTEM_PROMPT.format(
        pet_name=pet_name,
        pet_state=pet_state,
        user_emotion=user_emotion,
        memory=memory if memory else 'No previous sessions yet.',
        level=level
    )

    completion = client.chat.completions.create(
        model=MODEL,
        max_tokens=120,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message}
        ]
    )

    response_text = completion.choices[0].message.content.strip()

    # update memory
    memory_update = memory
    if len(memory) < 800:
        memory_update = memory + f"\nOwner said: '{user_message}' (looked {user_emotion}). {pet_name} replied: '{response_text[:60]}...'"
    else:
        lines = memory.split('\n')
        memory_update = '\n'.join(lines[-10:]) + f"\nOwner said: '{user_message}' (looked {user_emotion})."

    return response_text, memory_update
