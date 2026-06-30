def build_reply(message: str) -> dict:
    return {
        "reply": f"你刚才说的是{message}",
        "length": len(message)
    }

messages: list[dict] = []
messages.append({
    "role": "user",
    "content": "你好"
})
messages.append({
    "role": "assistant",
    "content": "你好，我是 AI 助手"
})

for item in messages:
    print(item["role"], item["content"])

print(build_reply("我要学习AI全栈"))