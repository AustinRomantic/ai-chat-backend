from collections.abc import Generator

from fastapi.testclient import TestClient

from app.services.llm_service import llm_service


def create_conversation(
    client: TestClient,
) -> str:
    response = client.post(
        "/conversations",
        json={
            "title": "Chat 自动化测试",
            "system_prompt": "你是测试助手。",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_non_stream_chat_persists_history(
    client: TestClient,
    monkeypatch,
) -> None:
    conversation_id = create_conversation(client)

    captured_calls: list[list[dict[str, str]]] = []

    def fake_chat(
        messages: list[dict[str, str]],
    ) -> str:
        captured_calls.append(messages)

        return f"第 {len(captured_calls)} 次模拟回答"

    monkeypatch.setattr(
        llm_service,
        "chat_with_messages",
        fake_chat,
    )

    first_response = client.post(
        "/chat",
        json={
            "conversation_id": conversation_id,
            "message": "请记住我喜欢 TypeScript。",
        },
    )

    assert first_response.status_code == 200
    assert (
        first_response.json()["reply"]
        == "第 1 次模拟回答"
    )

    second_response = client.post(
        "/chat",
        json={
            "conversation_id": conversation_id,
            "message": "我喜欢什么语言？",
        },
    )

    assert second_response.status_code == 200
    assert (
        second_response.json()["reply"]
        == "第 2 次模拟回答"
    )

    assert len(captured_calls) == 2

    second_llm_messages = captured_calls[1]

    assert [
        item["role"]
        for item in second_llm_messages
    ] == [
        "system",
        "user",
        "assistant",
        "user",
    ]

    history_response = client.get(
        f"/conversations/{conversation_id}/messages",
        params={
            "page": 1,
            "page_size": 20,
        },
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert history["total"] == 4

    assert [
        item["role"]
        for item in history["items"]
    ] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]


def test_stream_chat_persists_complete_answer(
    client: TestClient,
    monkeypatch,
) -> None:
    conversation_id = create_conversation(client)

    def fake_stream(
        messages: list[dict[str, str]],
    ) -> Generator[str, None, None]:
        yield "这是"
        yield "一条"
        yield "流式回答"

    monkeypatch.setattr(
        llm_service,
        "chat_with_messages_stream",
        fake_stream,
    )

    with client.stream(
        "POST",
        "/chat/stream",
        json={
            "conversation_id": conversation_id,
            "message": "请流式回答。",
        },
    ) as response:
        response_body = "".join(
            response.iter_text()
        )

    assert response.status_code == 200
    assert "event: message" in response_body
    assert "event: done" in response_body

    history_response = client.get(
        f"/conversations/{conversation_id}/messages",
        params={
            "page": 1,
            "page_size": 20,
        },
    )

    history = history_response.json()

    assert history["total"] == 2
    assert history["items"][0]["role"] == "user"
    assert history["items"][1]["role"] == "assistant"
    assert (
        history["items"][1]["content"]
        == "这是一条流式回答"
    )


def test_archived_conversation_rejects_chat(
    client: TestClient,
    monkeypatch,
) -> None:
    conversation_id = create_conversation(client)

    update_response = client.patch(
        f"/conversations/{conversation_id}",
        json={
            "status": "archived",
        },
    )

    assert update_response.status_code == 200

    response = client.post(
        "/chat",
        json={
            "conversation_id": conversation_id,
            "message": "归档后继续聊天。",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["error_code"]
        == "CONVERSATION_ARCHIVED"
    )

    history_response = client.get(
        f"/conversations/{conversation_id}/messages",
        params={
            "page": 1,
            "page_size": 20,
        },
    )

    assert history_response.json()["total"] == 0


def test_missing_conversation_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/chat",
        json={
            "conversation_id": (
                "00000000-0000-0000-0000-000000000000"
            ),
            "message": "不存在的会话。",
        },
    )

    assert response.status_code == 404
    assert (
        response.json()["error_code"]
        == "CONVERSATION_NOT_FOUND"
    )