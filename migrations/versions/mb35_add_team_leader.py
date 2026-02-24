"""add leader field to team

Revision ID: mb35addleader
Revises: mb34addteam
Create Date: 2026-02-24 15:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'mb35addleader'
down_revision = 'mb34addteam'
branch_labels = None
depends_on = None


def upgrade():
    # add nullable leader_id column and foreign key to user
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'leader_id' not in [c['name'] for c in insp.get_columns('team')]:
        op.add_column('team', sa.Column('leader_id', sa.Integer(), nullable=True))
        op.create_foreign_key('team_leader_fkey', 'team', 'user', ['leader_id'], ['id'])


def downgrade():
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'leader_id' in [c['name'] for c in insp.get_columns('team')]:
        op.drop_constraint('team_leader_fkey', 'team', type_='foreignkey')
        op.drop_column('team', 'leader_id')
