from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.user_repository import (
    create_user,
    get_user_by_email,
)


def main() -> None:
    with SessionLocal() as db:
        try:
            user = get_user_by_email(
                db=db,
                email=settings.dev_user_email,
            )

            if user is None:
                user = create_user(
                    db=db,
                    email=settings.dev_user_email,
                    display_name=settings.dev_user_display_name,
                )

                db.commit()

                print("dev_user_status=created")
            else:
                print("dev_user_status=already_exists")

            print(f"dev_user_id={user.id}")
            print(f"dev_user_email={user.email}")
            print(f"dev_user_display_name={user.display_name}")

        except SQLAlchemyError:
            db.rollback()
            raise


if __name__ == "__main__":
    main()