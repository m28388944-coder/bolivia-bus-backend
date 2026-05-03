"""add_support_tables
Revision ID: 4bc4446f448b
Revises: f1a5e812ae16
Create Date: 2026-05-01 07:53:21.388429
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '4bc4446f448b'
down_revision: Union[str, None] = 'f1a5e812ae16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE prioridadsoporte AS ENUM ('baja', 'media', 'alta', 'critica');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estadosoporte AS ENUM ('abierto', 'en_proceso', 'resuelto', 'cerrado');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            titulo VARCHAR(200) NOT NULL,
            descripcion TEXT NOT NULL,
            sistema VARCHAR(50) DEFAULT 'general',
            prioridad prioridadsoporte DEFAULT 'media',
            estado estadosoporte DEFAULT 'abierto',
            user_id UUID REFERENCES users(id),
            nota_interna TEXT,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS support_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticket_id UUID NOT NULL REFERENCES support_tickets(id),
            autor_id UUID REFERENCES users(id),
            autor_nombre VARCHAR(120) DEFAULT 'Sistema',
            autor_rol VARCHAR(20) DEFAULT 'developer',
            mensaje TEXT NOT NULL,
            es_nota_interna BOOLEAN DEFAULT false,
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)

def downgrade() -> None:
    op.execute('DROP TABLE IF EXISTS support_messages')
    op.execute('DROP TABLE IF EXISTS support_tickets')
    op.execute('DROP TYPE IF EXISTS estadosoporte')
    op.execute('DROP TYPE IF EXISTS prioridadsoporte')
