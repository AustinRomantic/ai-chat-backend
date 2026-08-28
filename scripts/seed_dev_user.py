from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User


def main() -> None:
    with SessionLocal() as db:
        try:
            statement = select(User).where(
                User.email == settings.dev_user_email
            )
            user = db.scalar(statement)

            if user is not None:
                print(f"开发用户已存在：id={user.id}, email={user.email}")
                return

            user = User(
                email=settings.dev_user_email,
                display_name=settings.dev_user_display_name,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            print(f"开发用户创建成功：id={user.id}, email={user.email}")

        except SQLAlchemyError:
            db.rollback()
            raise


if __name__ == "__main__":
    main()