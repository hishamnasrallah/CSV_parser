"""modify mapper set active date nullable

Revision ID: 338dd7156028
Revises: 6601c18f9d00
Create Date: 2023-03-19 14:12:55.713147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '338dd7156028'
down_revision = '6601c18f9d00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('processconfig', 'set_active_at', existing_type=sa.DateTime(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('processconfig', 'set_active_at', existing_type=sa.DateTime(), nullable=True)
    # ### end Alembic commands ###