import anthropic
import json
import os
import sys

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



MODES = {
    "tutor": "You are a helpful coding tutor. Be concise. User examples.",
    "review": "You are a senior code reviewer. Be critical but constructive. Point our bugs, style issues, and suggest improvements.",
    "explain": "You are an expert at explaining complex topics simply. Use analogies. Assume the reader is smart but unfamiliar with the topic",
    "debug": "You are a debugging expert. Ask clarifying questions, think step by step, and identify root causes."
}

current_mode = "tutor"
SYSTEM= MODES[current_mode]

while True:
    # user_input = sys.stdin.read()
    user_input = input("-->")
    if user_input.lower() == "quit":
        break
    if user_input.lower() == "clear":
        messages = []
        save_messages(messages)
        print("Chat history cleared.")
        continue
    if user_input.startswith("/mode"):
        parts = user_input.split()
        if len(parts) == 1:
            print(f"Current: {current_mode}")
            print(f"Available: {','.join(MODES.keys())}\n")
            continue
        mode = parts[1]
        if mode in MODES:
            current_mode = mode
            SYSTEM = MODES[current_mode]
            print(f"Switched to {mode} mode\n")
        else:
            print(f"Unknown mode. Available: {'.'.join(MODES.keys())}\n")
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