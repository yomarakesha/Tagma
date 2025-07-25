"""change additional_images column type

Revision ID: e83187d6a133
Revises: b1068b728da7
Create Date: 2025-07-13 10:23:09.089667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e83187d6a133'
down_revision = 'b1068b728da7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.alter_column('additional_images',
               existing_type=sa.TEXT(),
               type_=sa.PickleType(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog', schema=None) as batch_op:
        batch_op.alter_column('additional_images',
               existing_type=sa.PickleType(),
               type_=sa.TEXT(),
               existing_nullable=True)

    # ### end Alembic commands ###
