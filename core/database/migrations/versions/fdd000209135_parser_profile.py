"""parser profile

Revision ID: fdd000209135
Revises: 1412dd8fd8c0
Create Date: 2023-03-28 07:22:15.254565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdd000209135'
down_revision = '1412dd8fd8c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mapperprofile',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('mapper_id', sa.Integer(), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mapperprofile_id'), 'mapperprofile', ['id'], unique=True)
    op.create_index(op.f('ix_mapperprofile_mapper_id'), 'mapperprofile', ['mapper_id'], unique=False)
    op.create_index(op.f('ix_mapperprofile_profile_id'), 'mapperprofile', ['profile_id'], unique=False)
    op.create_table('profile',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('profile_name', sa.String(length=255), nullable=False),
    sa.Column('server_connection_username', sa.String(length=255), nullable=False),
    sa.Column('server_connection_password', sa.String(length=255), nullable=False),
    sa.Column('profile_description', sa.String(length=256), nullable=False),
    sa.Column('base_server_url', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_id'), 'profile', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_profile_id'), table_name='profile')
    op.drop_table('profile')
    op.drop_index(op.f('ix_mapperprofile_profile_id'), table_name='mapperprofile')
    op.drop_index(op.f('ix_mapperprofile_mapper_id'), table_name='mapperprofile')
    op.drop_index(op.f('ix_mapperprofile_id'), table_name='mapperprofile')
    op.drop_table('mapperprofile')
    # ### end Alembic commands ###
