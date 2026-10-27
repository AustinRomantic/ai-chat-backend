"""Add nullable password_hash for existing users."""

from alembic import op
import sqlalchemy as sa


revision = "20261027a001"
down_revision = "1026c78a0231"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "password_hash",
    )