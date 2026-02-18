import anthropic
import json
import os

HISTORY_FILE = "chat_history.json"

client = anthropic.Anthropic()

def load_messages():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

messages = load_messages()

if messages:
    print(f"Loaded {len(messages)} messages from history.")
else:
    print("Starting new chat.")

print("Command line chatbot with claude. Type 'quit' to end. Type 'clear' to clear history.")

SYSTEM = "You are a helpful coding tutor. Be concise. User examples."

while True:
    user_input = input("You:")
    if user_input.lower() == "quit":
        break
    if user_input.lower() == "clear":
        messages = []
        save_messages(messages)
        print("Chat history cleared.")
        continue
    
    messages.append({"role": "user", "content": user_input})

    assistant_msg = ""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
        system=SYSTEM
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            assistant_msg += text

    print("\n")
    messages.append({"role": "assistant","content": assistant_msg})
    save_messages(messages)