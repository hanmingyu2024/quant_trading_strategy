"""创建密码历史记录表

修订ID: 1234567890ab
上一个修订: previous_revision_id
创建日期: 2024-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # 创建密码历史表
    op.create_table(
        'password_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_history_user_id', 'password_history', ['user_id'])

def downgrade():
    op.drop_index('ix_password_history_user_id', 'password_history')
    op.drop_table('password_history') 