"""create_scoring_audit_and_evaluations_tables

Revision ID: aa5eafac932b
Revises: 28c8d4515cbf
Create Date: 2026-09-17 11:13:43.830213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa5eafac932b'
down_revision: Union[str, Sequence[str], None] = '28c8d4515cbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('lead_scores', sa.Column('conversion_probability', sa.Float(), nullable=True))

    op.create_table(
        'scoring_runs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.String(length=32), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('leads_scored', sa.Integer(), nullable=False),
        sa.Column('high_priority_count', sa.Integer(), nullable=False),
        sa.Column('medium_priority_count', sa.Integer(), nullable=False),
        sa.Column('low_priority_count', sa.Integer(), nullable=False),
        sa.Column('average_score', sa.Float(), nullable=False),
        sa.Column('execution_type', sa.String(length=32), server_default='manual', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='COMPLETED', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scoring_runs_company_id', 'scoring_runs', ['company_id'], unique=False)
    op.create_index('ix_scoring_runs_company_started', 'scoring_runs', ['company_id', 'started_at'], unique=False)

    op.create_table(
        'model_evaluations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('dataset_name', sa.String(length=100), nullable=False),
        sa.Column('evaluation_type', sa.String(length=50), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=False),
        sa.Column('train_size', sa.Integer(), nullable=False),
        sa.Column('test_size', sa.Integer(), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('limitations', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_model_evaluations_version', 'model_evaluations', ['model_version'], unique=False)
    op.create_index('ix_model_evaluations_created_at', 'model_evaluations', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_model_evaluations_created_at', table_name='model_evaluations')
    op.drop_index('ix_model_evaluations_version', table_name='model_evaluations')
    op.drop_table('model_evaluations')

    op.drop_index('ix_scoring_runs_company_started', table_name='scoring_runs')
    op.drop_index('ix_scoring_runs_company_id', table_name='scoring_runs')
    op.drop_table('scoring_runs')

    op.drop_column('lead_scores', 'conversion_probability')

