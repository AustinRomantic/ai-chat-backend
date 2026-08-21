import uuid

from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.conversation_repository import (
    create_conversation,
    delete_conversation,
    get_conversation_by_id,
)
from app.repositories.message_repository import (
    create_message,
    list_messages_by_conversation,
)
from app.repositories.user_repository import get_user_by_email


def create_and_commit_conversation() -> uuid.UUID:
    with SessionLocal() as db:
        try:
            user = get_user_by_email(
                db=db,
                email=settings.dev_user_email,
            )

            if user is None:
                raise RuntimeError(
                    "开发用户不存在，请先运行 scripts.seed_dev_user"
                )

            conversation = create_conversation(
                db=db,
                user_id=user.id,
                title=f"Day 18 ORM 测试会话 {uuid.uuid4().hex[:8]}",
                system_prompt="你是一个耐心的 PostgreSQL 学习助手。",
            )

            create_message(
                db=db,
                conversation_id=conversation.id,
                role="user",
                content="什么是 ORM 查询？",
            )

            create_message(
                db=db,
                conversation_id=conversation.id,
                role="assistant",
                content="ORM 查询是使用 Python Model 描述数据库查询。",
            )

            print(f"before_commit_conversation_id={conversation.id}")

            db.commit()

            print("transaction_commit=success")

            return conversation.id

        except Exception:
            db.rollback()
            raise


def read_conversation(
    conversation_id: uuid.UUID,
) -> None:
    with SessionLocal() as db:
        conversation = get_conversation_by_id(
            db=db,
            conversation_id=conversation_id,
        )

        if conversation is None:
            raise RuntimeError("测试会话不存在")

        messages = list_messages_by_conversation(
            db=db,
            conversation_id=conversation.id,
        )

        print(f"conversation_title={conversation.title}")
        print(f"conversation_user_email={conversation.user.email}")
        print(f"message_count={len(messages)}")

        for message in messages:
            print(
                f"message_role={message.role} "
                f"message_content={message.content}"
            )


def test_transaction_rollback() -> None:
    attempted_conversation_id: uuid.UUID | None = None

    with SessionLocal() as db:
        try:
            user = get_user_by_email(
                db=db,
                email=settings.dev_user_email,
            )

            if user is None:
                raise RuntimeError("开发用户不存在")

            conversation = create_conversation(
                db=db,
                user_id=user.id,
                title="这条会话最终不应该存在",
            )

            attempted_conversation_id = conversation.id

            create_message(
                db=db,
                conversation_id=conversation.id,
                role="user",
                content="第一条合法消息",
            )

            create_message(
                db=db,
                conversation_id=conversation.id,
                role="system",
                content="这条消息会违反 role 检查约束",
            )

            db.commit()

            raise RuntimeError("非法消息意外写入成功")

        except IntegrityError:
            db.rollback()
            print("transaction_rollback=executed")

    if attempted_conversation_id is None:
        raise RuntimeError("没有生成待验证的会话 ID")

    with SessionLocal() as db:
        conversation = get_conversation_by_id(
            db=db,
            conversation_id=attempted_conversation_id,
        )

        if conversation is not None:
            raise RuntimeError("事务回滚失败，会话仍然存在")

        print("rollback_verification=passed")


def cleanup_conversation(
    conversation_id: uuid.UUID,
) -> None:
    with SessionLocal() as db:
        try:
            conversation = get_conversation_by_id(
                db=db,
                conversation_id=conversation_id,
            )

            if conversation is None:
                raise RuntimeError("待清理的会话不存在")

            delete_conversation(
                db=db,
                conversation=conversation,
            )

            db.commit()

            print("conversation_delete=committed")

        except Exception:
            db.rollback()
            raise

    with SessionLocal() as db:
        conversation = get_conversation_by_id(
            db=db,
            conversation_id=conversation_id,
        )

        messages = list_messages_by_conversation(
            db=db,
            conversation_id=conversation_id,
        )

        if conversation is not None:
            raise RuntimeError("会话删除失败")

        if messages:
            raise RuntimeError("消息级联删除失败")

        print("cascade_delete_verification=passed")


def main() -> None:
    conversation_id = create_and_commit_conversation()

    read_conversation(conversation_id)

    cleanup_conversation(conversation_id)

    test_transaction_rollback()

    print("orm_test=completed")


if __name__ == "__main__":
    main()