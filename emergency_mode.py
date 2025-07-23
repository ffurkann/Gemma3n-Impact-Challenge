import ollama
import json
from rapidfuzz import process, fuzz


def get_knowledge_emergency(user_input):
    try:
        with open('Knowledge/knowledge_emergency.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        return None

    entries = [(entry["symptoms"], entry) for entry in knowledge]
    symptom_texts = [s for s, _ in entries]

    match_result = process.extractOne(user_input, symptom_texts, scorer=fuzz.partial_ratio)
    if match_result is None:
        return None
    best_match, score, _ = match_result

    if score >= 60:
        for s, entry in entries:
            if s == best_match:
                return entry
    return None


def make_input_emergency(user_input):
    knowledge_entry = get_knowledge_emergency(user_input)
    knowledge_text = "Knowledge:\n"
    if knowledge_entry:
        for key, value in knowledge_entry.items():
            knowledge_text += f"{key}: {value}\n"
    else:
        knowledge_text += "No matching condition found. Use basic emergency medical logic.\n"

    starter_text = (
        "You are helping in an emergency situation that requires first aid. "
        "Your responses must be as simple, short, and clear as possible. Every second counts.\n"
        "You must tell them what to do in terms of first aid too not just call 911.\n"
    )
    return f"{starter_text}{knowledge_text}\nUser input: {user_input}"


def emergency_chat_with_text(user_input):
    prompt = make_input_emergency(user_input)
    response = ollama.chat(
        model='gemma3n:e4b',
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']


if __name__ == "__main__":
    user_input = input("Emergency input: ")
    print(emergency_chat_with_text(user_input))
