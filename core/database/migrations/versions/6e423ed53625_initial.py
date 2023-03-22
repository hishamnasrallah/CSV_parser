"""initial

Revision ID: 6e423ed53625
Revises: 
Create Date: 2023-02-20 13:50:44.606119

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e423ed53625'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('filereceivehistory',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('file_size_kb', sa.BigInteger(), nullable=True),
    sa.Column('file_name_as_received', sa.String(length=255), nullable=True),
    sa.Column('task_id', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_filereceivehistory_file_id'), 'filereceivehistory', ['file_id'], unique=False)
    op.create_index(op.f('ix_filereceivehistory_id'), 'filereceivehistory', ['id'], unique=True)
    op.create_table('processconfig',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_path', sa.String(length=255), nullable=True),
    sa.Column('frequency', sa.Enum('min_1', 'min_15', 'min_30', 'hour_1', 'hour_2', 'hour_3', 'hour_6', 'hour_12', 'hour_24', name='frequency'), nullable=True),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('process_id', sa.Integer(), nullable=True),
    sa.Column('last_run', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processconfig_id'), 'processconfig', ['id'], unique=True)
    op.create_table('processmapfield',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.Column('field_name', sa.String(length=255), nullable=True),
    sa.Column('map_field_name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_processmapfield_file_id'), 'processmapfield', ['file_id'], unique=False)
    op.create_index(op.f('ix_processmapfield_id'), 'processmapfield', ['id'], unique=True)
    op.create_table('celery_taskmeta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_id', sa.String(length=155), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('result', sa.PickleType(), nullable=True),
    sa.Column('date_done', sa.DateTime(), nullable=True),
    sa.Column('traceback', sa.Text(), nullable=True),
    sa.Column('name', sa.String(length=155), nullable=True),
    sa.Column('args', sa.LargeBinary(), nullable=True),
    sa.Column('kwargs', sa.LargeBinary(), nullable=True),
    sa.Column('worker', sa.String(length=155), nullable=True),
    sa.Column('retries', sa.Integer(), nullable=True),
    sa.Column('queue', sa.String(length=155), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('task_id'),
    sqlite_autoincrement=True
    )
    op.create_table('celery_tasksetmeta',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('taskset_id', sa.String(length=155), nullable=True),
    sa.Column('result', sa.PickleType(), nullable=True),
    sa.Column('date_done', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('taskset_id'),
    sqlite_autoincrement=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('celery_tasksetmeta')
    op.drop_table('celery_taskmeta')
    op.drop_index(op.f('ix_processmapfield_id'), table_name='processmapfield')
    op.drop_index(op.f('ix_processmapfield_file_id'), table_name='processmapfield')
    op.drop_table('processmapfield')
    op.drop_index(op.f('ix_processconfig_id'), table_name='processconfig')
    op.drop_table('processconfig')
    op.drop_index(op.f('ix_filereceivehistory_id'), table_name='filereceivehistory')
    op.drop_index(op.f('ix_filereceivehistory_file_id'), table_name='filereceivehistory')
    op.drop_table('filereceivehistory')
    # ### end Alembic commands ###
