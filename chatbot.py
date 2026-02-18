import anthropic

client = anthropic.Anthropic()

messages = []

print("Chat with claude")

while True:
    user_input = input("You:")
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})

    assistant_msg = ""

    with client.messages.stream(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
        system="You are a private who only speaks in rhymes."
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            assistant_msg += text

    print("\n")
    messages.append({"role": "assistant","content": assistant_msg})