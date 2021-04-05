"""empty message

Revision ID: 791012b3b391
Revises: d2032aac8176
Create Date: 2021-04-03 17:09:19.788887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '791012b3b391'
down_revision = 'd2032aac8176'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shows', 'id',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('shows', 'id',
               existing_type=sa.INTEGER(),
               server_default=sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
               existing_nullable=False,
               autoincrement=True)
    # ### end Alembic commands ###