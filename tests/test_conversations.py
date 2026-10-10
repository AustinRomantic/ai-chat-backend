from fastapi.testclient import TestClient


def test_conversation_crud(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/conversations",
        json={
            "title": "pytest 会话",
            "system_prompt": "你是测试助手。",
        },
    )

    assert create_response.status_code == 201

    created_conversation = create_response.json()
    conversation_id = created_conversation["id"]

    assert created_conversation["title"] == "pytest 会话"
    assert created_conversation["status"] == "active"

    list_response = client.get(
        "/conversations",
        params={
            "page": 1,
            "page_size": 20,
        },
    )

    assert list_response.status_code == 200

    conversation_list = list_response.json()

    assert conversation_list["total"] == 1
    assert len(conversation_list["items"]) == 1

    detail_response = client.get(
        f"/conversations/{conversation_id}"
    )

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == conversation_id

    update_response = client.patch(
        f"/conversations/{conversation_id}",
        json={
            "title": "更新后的 pytest 会话",
            "status": "archived",
        },
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["title"]
        == "更新后的 pytest 会话"
    )
    assert update_response.json()["status"] == "archived"

    delete_response = client.delete(
        f"/conversations/{conversation_id}"
    )

    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/conversations/{conversation_id}"
    )

    assert missing_response.status_code == 404
    assert (
        missing_response.json()["error_code"]
        == "CONVERSATION_NOT_FOUND"
    )


def test_conversation_pagination(
    client: TestClient,
) -> None:
    for index in range(3):
        response = client.post(
            "/conversations",
            json={
                "title": f"分页测试会话 {index + 1}",
            },
        )

        assert response.status_code == 201

    first_page_response = client.get(
        "/conversations",
        params={
            "page": 1,
            "page_size": 2,
        },
    )

    first_page = first_page_response.json()

    assert first_page["total"] == 3
    assert len(first_page["items"]) == 2

    second_page_response = client.get(
        "/conversations",
        params={
            "page": 2,
            "page_size": 2,
        },
    )

    second_page = second_page_response.json()

    assert second_page["total"] == 3
    assert len(second_page["items"]) == 1