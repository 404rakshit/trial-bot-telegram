"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create use_case_templates table
    op.create_table('use_case_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('hours_ahead', sa.Integer(), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_use_case_templates_is_active', 'use_case_templates', ['is_active'], unique=False)

    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.BigInteger(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id')
    )
    op.create_index('ix_users_chat_id', 'users', ['chat_id'], unique=True)
    op.create_index('ix_users_location', 'users', ['latitude', 'longitude'], unique=False)

    # Create reminders table
    op.create_table('reminders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('hours_ahead', sa.Integer(), nullable=False),
        sa.Column('custom_message', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_alerted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['use_case_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'], unique=False)
    op.create_index('ix_reminders_is_active', 'reminders', ['is_active'], unique=False)
    op.create_index('ix_reminders_user_active', 'reminders', ['user_id', 'is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_reminders_user_active', table_name='reminders')
    op.drop_index('ix_reminders_is_active', table_name='reminders')
    op.drop_index('ix_reminders_user_id', table_name='reminders')
    op.drop_table('reminders')

    op.drop_index('ix_users_location', table_name='users')
    op.drop_index('ix_users_chat_id', table_name='users')
    op.drop_table('users')

    op.drop_index('ix_use_case_templates_is_active', table_name='use_case_templates')
    op.drop_table('use_case_templates')
