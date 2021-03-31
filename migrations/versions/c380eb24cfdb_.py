"""empty message

Revision ID: c380eb24cfdb
Revises: 7d941961d384
Create Date: 2021-03-31 10:41:17.453472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c380eb24cfdb'
down_revision = '7d941961d384'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=False))
    op.drop_column('Artist', 'looking_venues')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('looking_venues', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Artist', 'seeking_venue')
    # ### end Alembic commands ###
