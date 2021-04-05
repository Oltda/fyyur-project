"""empty message

Revision ID: 1ba66d49b16d
Revises: 791012b3b391
Create Date: 2021-04-03 17:11:34.314047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ba66d49b16d'
down_revision = '791012b3b391'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website_link')
    # ### end Alembic commands ###