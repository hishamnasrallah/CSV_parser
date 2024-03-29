"""modify mapper field

Revision ID: 0a817bb81ca9
Revises: 6e423ed53625
Create Date: 2023-02-21 15:35:57.312988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a817bb81ca9'
down_revision = '6e423ed53625'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('processmapfield', sa.Column('is_ignored', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('processmapfield', 'is_ignored')
    # ### end Alembic commands ###
