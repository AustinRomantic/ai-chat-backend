from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT
                        1 AS database_health,
                        current_database() AS database_name,
                        current_user AS database_role
                    """
                )
            ).mappings().one()

            print(f"database_health={result['database_health']}")
            print(f"database_name={result['database_name']}")
            print(f"database_role={result['database_role']}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()