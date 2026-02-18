import anthropic
import json
import os
import sys
import datetime

HISTORY_FILE = "chat_history.json"
MARKDOWN_FILE="chat_history.md"

client = anthropic.Anthropic()

def load_messages():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def save_markdown(messages):
    with open(MARKDOWN_FILE, "w") as f:
        for message in messages:
            if "timestamp" in message:
                f.write(f"{message['timestamp']}\n")
            f.write(f"{message['role']}: {message['content']}\n")
            f.write("\n")

messages = load_messages()
current_usage_input = 0
current_usage_output = 0

if messages:
    print(f"Loaded {len(messages)} messages from history.")
else:
    print("Starting new chat.")

print("Command line chatbot with claude. Type 'quit' to end. Type 'clear' to clear history.")



MODES = {
    "tutor": "You are a helpful coding tutor. Be concise. User examples.",
    "review": "You are a senior code reviewer. Be critical but constructive. Point our bugs, style issues, and suggest improvements.",
    "explain": "You are an expert at explaining complex topics simply. Use analogies. Assume the reader is smart but unfamiliar with the topic",
    "debug": "You are a debugging expert. Ask clarifying questions, think step by step, and identify root causes.",
    "gorden-ramsay": "You are the gorden-ramsey of code reviews. Be honest and demanding. Expect perfection in the craft.",
    "interview": "You are conducting a mock technical interview. Ask one question at a time. Wait for your answer. Give feedback before moving to the next question. Cover Python, data structures, and system design."
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
    if user_input.startswith("/usage"):
        print(f"Current usage: {current_usage_input} input tokens, {current_usage_output} output tokens, total: {current_usage_input + current_usage_output}")
        print(f"Cost: {current_usage_input * 0.000003 + current_usage_output * 0.000015} USD")
        continue
    if user_input.startswith("/summary"):
        temp = messages.copy()
        temp.append({"role": "user", "content": "Summarize this conversation in 3 bullet points"})
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[ {"role": message["role"], "content": message["content"]} for message in temp],
        ) as stream:
            for text in stream.text_stream:
                
                print(text, end="", flush=True)
        final_message = stream.get_final_message()
        print("\n")
        current_usage_input += final_message.usage.input_tokens 
        current_usage_output += final_message.usage.output_tokens
        continue
    if user_input.startswith("/export"):
        save_markdown(messages)
        print("Chat history exported to chat_history.md")
        continue
    if user_input.startswith("/interview"):
        messages.append({"role": "user", "content": "You are conducting a mock technical interview. Ask one question at a time. Wait for your answer. Give feedback before moving to the next question. Cover Python, data structures, and system design.", "timestamp": datetime.datetime.now().isoformat()})
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[ {"role": message["role"], "content": message["content"]} for message in messages],
        ) as stream:
            for text in stream.text_stream:
                
                print(text, end="", flush=True)
        final_message = stream.get_final_message()
        print("\n")
        current_usage_input += final_message.usage.input_tokens 
        current_usage_output += final_message.usage.output_tokens
        continue
    messages.append({"role": "user", "content": user_input, "timestamp": datetime.datetime.now().isoformat()})

    assistant_msg = ""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[ {"role": message["role"], "content": message["content"]} for message in messages],
        system=SYSTEM,
    ) as stream:
        for text in stream.text_stream:
            
            print(text, end="", flush=True)
            assistant_msg += text
    final_message = stream.get_final_message()
    current_usage_input += final_message.usage.input_tokens 
    current_usage_output += final_message.usage.output_tokens
    print("\n")
    messages.append({"role": "assistant","content": assistant_msg, "timestamp": datetime.datetime.now().isoformat()})
    save_messages(messages)