"""add business state currency and payroll paid status

Revision ID: 11e08ff27181
Revises: 9721a7b3ec06
Create Date: 2026-07-28 21:45:10.156112

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "11e08ff27181"
down_revision: str | None = "9721a7b3ec06"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("businesses", sa.Column("state", sa.String(length=120), nullable=True))
    op.add_column(
        "businesses",
        sa.Column("currency", sa.String(length=8), server_default="INR", nullable=False),
    )
    # Add the 'paid' value to the payroll_status_enum. ``ALTER TYPE ... ADD VALUE``
    # cannot run inside a transaction, so we commit the current transaction first.
    op.execute("COMMIT")
    op.execute("ALTER TYPE payroll_status_enum ADD VALUE IF NOT EXISTS 'paid'")


def downgrade() -> None:
    """Downgrade schema."""
    # NOTE: PostgreSQL does not support removing an individual enum value.
    # Removing 'paid' would require recreating the type; left as a no-op.
    op.drop_column("businesses", "currency")
    op.drop_column("businesses", "state")
