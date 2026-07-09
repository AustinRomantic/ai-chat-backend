from app.services.llm_service import llm_service


def main():
    reply = llm_service.chat(
        message="用一句话介绍 FastAPI 是什么",
        system_prompt="你是一个擅长用大白话解释技术概念的 AI 助手。"
    )

    print("模型返回：")
    print(reply)


if __name__ == "__main__":
    main()