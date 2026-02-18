import anthropic

client = anthropic.Anthropic()

messages = []

print("Chat with claude")

while True:
    user_input = input("You:")
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=messages,
    )

    assistant_msg = response.content[0].text
    messages.append({"role": "assistant","content": assistant_msg})

    print(f"\nClaude: {assistant_msg}\n")