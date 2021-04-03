"""empty message

Revision ID: 83449505db2a
Revises: 1ba66d49b16d
Create Date: 2021-04-03 17:17:59.079432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83449505db2a'
down_revision = '1ba66d49b16d'
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
    # ### end Alembic commands ###
