"""add_developer_role
Revision ID: f1a5e812ae16
Revises: 93a135d5e6d2
Create Date: 2026-05-01 07:28:42.341568
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f1a5e812ae16'
down_revision: Union[str, None] = '93a135d5e6d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("ALTER TYPE rolusuario ADD VALUE IF NOT EXISTS 'developer'")

def downgrade() -> None:
    pass
