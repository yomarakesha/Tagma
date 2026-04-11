"""add order to client and partner

Revision ID: a3f9c1e2d4b5
Revises: e83187d6a133
Create Date: 2026-04-11 09:48:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f9c1e2d4b5'
down_revision = 'e83187d6a133'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=True, server_default='0'))

    with op.batch_alter_table('partner', schema=None) as batch_op:
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=True, server_default='0'))


def downgrade():
    with op.batch_alter_table('partner', schema=None) as batch_op:
        batch_op.drop_column('order')

    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('order')
