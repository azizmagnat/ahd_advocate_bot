"""add ai classification fields

Revision ID: 003
Revises: 002
Create Date: 2026-02-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add AI classification columns to questions table
    op.add_column('questions', sa.Column('complexity', sa.String(), nullable=True))
    op.add_column('questions', sa.Column('ai_confidence', sa.Float(), nullable=True))
    op.add_column('questions', sa.Column('category', sa.String(), nullable=True))
    op.add_column('questions', sa.Column('auto_answered', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('questions', sa.Column('requires_human', sa.Boolean(), nullable=True, server_default='false'))


def downgrade() -> None:
    # Remove AI classification columns
    op.drop_column('questions', 'requires_human')
    op.drop_column('questions', 'auto_answered')
    op.drop_column('questions', 'category')
    op.drop_column('questions', 'ai_confidence')
    op.drop_column('questions', 'complexity')
