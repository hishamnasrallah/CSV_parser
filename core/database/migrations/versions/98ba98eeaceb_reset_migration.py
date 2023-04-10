"""reset migration

Revision ID: 98ba98eeaceb
Revises: fdd000209135
Create Date: 2023-04-05 23:28:48.255895

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98ba98eeaceb'
down_revision = 'fdd000209135'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('profile', 'company_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('profile', 'company_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###