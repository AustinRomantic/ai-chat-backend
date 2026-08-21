from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def create_user(
    db: Session,
    email: str,
    display_name: str,
) -> User:
    user = User(
        email=email,
        display_name=display_name,
    )

    db.add(user)
    db.flush()
    db.refresh(user)

    return user
