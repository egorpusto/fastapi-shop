"""change_is_active_to_boolean

Revision ID: b52c1dd588e9
Revises: 58f7e2d6b31f
Create Date: 2026-02-17 19:42:53.809606+00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b52c1dd588e9'
down_revision = '58f7e2d6b31f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'categories',
        'is_active',
        existing_type=sa.INTEGER(),
        type_=sa.Boolean(),
        nullable=False,
        postgresql_using='is_active::boolean',
    )
    op.alter_column(
        'products',
        'is_active',
        existing_type=sa.INTEGER(),
        type_=sa.Boolean(),
        nullable=False,
        postgresql_using='is_active::boolean',
    )


def downgrade() -> None:
    op.alter_column(
        'products',
        'is_active',
        existing_type=sa.Boolean(),
        type_=sa.INTEGER(),
        nullable=False,
        postgresql_using='is_active::integer',
    )
    op.alter_column(
        'categories',
        'is_active',
        existing_type=sa.Boolean(),
        type_=sa.INTEGER(),
        nullable=False,
        postgresql_using='is_active::integer',
    )