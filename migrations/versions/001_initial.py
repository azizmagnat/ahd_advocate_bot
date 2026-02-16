"""initial migration

Revision ID: 001
Revises: 
Create Date: 2026-02-16 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    
    # Create enums with error handling for duplicates
    try:
        conn.execute(sa.text("CREATE TYPE userrole AS ENUM ('user', 'admin')"))
    except ProgrammingError:
        pass  # Type already exists
    
    try:
        conn.execute(sa.text("CREATE TYPE questionstatus AS ENUM ('pending', 'paid', 'answered')"))
    except ProgrammingError:
        pass  # Type already exists
    
    try:
        conn.execute(sa.text("CREATE TYPE paymentstatus AS ENUM ('pending', 'confirmed', 'rejected')"))
    except ProgrammingError:
        pass  # Type already exists

    # Check if tables already exist before creating
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'users' not in existing_tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('telegram_id', sa.BigInteger(), nullable=False),
            sa.Column('role', postgresql.ENUM('user', 'admin', name='userrole', create_type=False), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)

    if 'questions' not in existing_tables:
        op.create_table(
            'questions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('answer', sa.Text(), nullable=True),
            sa.Column('status', postgresql.ENUM('pending', 'paid', 'answered', name='questionstatus', create_type=False), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)

    if 'payments' not in existing_tables:
        op.create_table(
            'payments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('question_id', sa.Integer(), nullable=True),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('proof_file_id', sa.String(), nullable=False),
            sa.Column('status', postgresql.ENUM('pending', 'confirmed', 'rejected', name='paymentstatus', create_type=False), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('question_id')
        )
        op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    conn = op.get_bind()
    try:
        conn.execute(sa.text('DROP TYPE paymentstatus'))
    except:
        pass
    try:
        conn.execute(sa.text('DROP TYPE questionstatus'))
    except:
        pass
    try:
        conn.execute(sa.text('DROP TYPE userrole'))
    except:
        pass
