"""add payment method fields

Revision ID: 002_payment_fields
Revises: 001_initial
Create Date: 2026-02-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_payment_fields'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to payments table
    op.add_column('payments', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('payments', sa.Column('invoice_id', sa.String(), nullable=True))
    op.add_column('payments', sa.Column('payment_url', sa.String(), nullable=True))
    
    # Update existing records to have 'manual' as default
    op.execute("UPDATE payments SET payment_method = 'manual' WHERE payment_method IS NULL")
    
    # Make proof_file_id nullable (for online payments)
    op.alter_column('payments', 'proof_file_id', nullable=True)


def downgrade() -> None:
    # Remove added columns
    op.drop_column('payments', 'payment_url')
    op.drop_column('payments', 'invoice_id')
    op.drop_column('payments', 'payment_method')
    
    # Revert proof_file_id to not nullable
    op.alter_column('payments', 'proof_file_id', nullable=False)
