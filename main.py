import ollama
import json
import time
import datetime
from rapidfuzz import process, fuzz

def get_knowledge_main(user_input):
    try:
        with open('Knowledge/knowledge_main.json', 'r') as f:
            knowledge = json.load(f)
    except FileNotFoundError:
        return None

    symptom_list = [(entry["symptoms"], entry) for entry in knowledge]
    symptom_texts = [symp for symp, _ in symptom_list]
    best_match, score, _ = process.extractOne(user_input, symptom_texts, scorer=fuzz.token_sort_ratio)

    if score >= 70:
        for symp, entry in symptom_list:
            if symp == best_match:
                return entry
    return None

def make_input_main(user_input):
    starting_part = (
        "Please try to use the knowledge given to you mostly and try to incorporate the memory to make it more personalized.\n"
        "The memory has time stamps and you will be given the current time so try to incorporate that to the answer when it's needed.\n"
    )
    ending_part = (
        "Your response should be in the following format:\n"
        "{answer}your answer here{/answer},\n"
        "{memory}what to add to the memory{/memory}"
    )
    try:
        with open("Memory/memory_main.json", "r", encoding="utf-8") as f:
            memory = json.load(f)
    except FileNotFoundError:
        memory = {}

    knowledge_entry = get_knowledge_main(user_input)
    knowledge_text = "Knowledge:\n"
    if knowledge_entry:
        for key, value in knowledge_entry.items():
            knowledge_text += f"{key}: {value}\n"
    else:
        knowledge_text = (
            "Knowledge:\n"
            "No matching condition found. You may use your own medical reasoning and comfort suggestions to help the user.\n"
        )

    today = datetime.date.today()
    current_time = datetime.datetime.now().strftime('%H:%M')
    memory_text = "Memory:\n"
    for key in memory.keys():
        try:
            key_date = datetime.datetime.strptime(key, "%Y-%m-%d").date()
            if (today - key_date).days < 7:
                memory_text += f"{key}: {memory[key]}\n"
        except ValueError:
            continue
    memory_text += "\n"

    final_prompt = f"{starting_part}Current Time: {current_time}\n{knowledge_text}{memory_text}User input: {user_input}\n{ending_part}"
    return final_prompt

def ask_gemma(prompt):
    response = ollama.chat(
        model='gemma3n:e4b',
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

def parse_response(text):
    def extract(tag):
        start = text.find(f"{{{tag}}}") + len(tag) + 2
        end = text.find(f"{{/{tag}}}")
        return text[start:end].strip()
    return extract("answer"), extract("memory")

def update_memory(path, new_entry):
    try:
        with open(path, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except:
        memory = {}
    today = str(datetime.date.today())
    memory[today] = memory.get(today, "") + "\n" + new_entry
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def chat_loop():
    memory_path = "Memory/memory_main.json"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        prompt = make_input_main(user_input)
        response = ask_gemma(prompt)
        answer, memory_update = parse_response(response)
        print(f"\nGemma: {answer}\n")
        update_memory(memory_path, memory_update)

if __name__ == "__main__":
    chat_loop()
