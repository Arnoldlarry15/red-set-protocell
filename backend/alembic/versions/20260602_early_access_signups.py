"""create early access signups table

Revision ID: 20260602_early_access_signups
Revises:
Create Date: 2026-06-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260602_early_access_signups"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "early_access_signups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_early_access_signups_email", "early_access_signups", ["email"], unique=True)
    op.create_index("ix_early_access_signups_role", "early_access_signups", ["role"], unique=False)
    op.create_index("ix_early_access_signups_status", "early_access_signups", ["status"], unique=False)
    op.create_index("ix_early_access_signups_submitted_at", "early_access_signups", ["submitted_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_early_access_signups_submitted_at", table_name="early_access_signups")
    op.drop_index("ix_early_access_signups_status", table_name="early_access_signups")
    op.drop_index("ix_early_access_signups_role", table_name="early_access_signups")
    op.drop_index("ix_early_access_signups_email", table_name="early_access_signups")
    op.drop_table("early_access_signups")
