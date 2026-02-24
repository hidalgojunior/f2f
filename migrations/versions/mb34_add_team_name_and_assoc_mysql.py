"""mysql fix: add team.nome and team_user table

Revision ID: mb34addteam
Revises: 3e3a64950a2f
Create Date: 2026-02-24 13:10:00.000000
Note: this migration ensures the `team.nome` column exists and creates
an association table `team_user` for the many-to-many relationship
between teams and users.  Early iterations of the admin routes
attempted to delete teams by `event_id`, which isn’t a real column in
the schema; that mistake caused 500 errors on event deletion.  The
problem was fixed in application code, but the migration remains for
historical context and to allow fresh installs to initialize correctly."""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'mb34addteam'
down_revision = '3e3a64950a2f'
branch_labels = None
depends_on = None


def upgrade():
    # add nome column if missing
    conn = op.get_bind()
    insp = sa.inspect(conn)
    cols = [c['name'] for c in insp.get_columns('team')]
    if 'nome' not in cols:
        op.add_column('team', sa.Column('nome', sa.String(120), nullable=False, server_default=''))
        # remove default after creation
        op.alter_column('team', 'nome', server_default=None)
    # create association table if not exists
    if not insp.has_table('team_user'):
        op.create_table('team_user',
            sa.Column('team_id', sa.Integer(), sa.ForeignKey('team.id'), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), primary_key=True)
        )


def downgrade():
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if insp.has_table('team_user'):
        op.drop_table('team_user')
    cols = [c['name'] for c in insp.get_columns('team')]
    if 'nome' in cols:
        op.drop_column('team', 'nome')
