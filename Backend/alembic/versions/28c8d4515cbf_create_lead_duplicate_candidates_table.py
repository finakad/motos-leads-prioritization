"""create_lead_duplicate_candidates_table

Revision ID: 28c8d4515cbf
Revises: 48102b1244e8
Create Date: 2026-09-17 10:53:17.921344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28c8d4515cbf'
down_revision: Union[str, Sequence[str], None] = '48102b1244e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'lead_duplicate_candidates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.String(length=32), nullable=False),
        sa.Column('primary_lead_id', sa.String(length=20), nullable=False),
        sa.Column('duplicate_lead_id', sa.String(length=20), nullable=False),
        sa.Column('confidence_tier', sa.String(length=32), nullable=False),
        sa.Column('match_score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('match_reasons', sa.JSON(), nullable=False),
        sa.Column('evidence_payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='SUGERIDO', nullable=False),
        sa.Column('decision', sa.String(length=32), server_default='PENDIENTE', nullable=False),
        sa.Column('decision_by', sa.String(length=100), nullable=True),
        sa.Column('decision_notes', sa.Text(), nullable=True),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['duplicate_lead_id'], ['leads.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['primary_lead_id'], ['leads.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'primary_lead_id', 'duplicate_lead_id', name='uq_lead_duplicates_pair'),
        sa.CheckConstraint('primary_lead_id <> duplicate_lead_id', name='ck_lead_duplicates_distinct'),
    )
    op.create_index('ix_lead_duplicate_candidates_company_id', 'lead_duplicate_candidates', ['company_id'], unique=False)
    op.create_index('ix_lead_duplicate_candidates_primary_lead_id', 'lead_duplicate_candidates', ['primary_lead_id'], unique=False)
    op.create_index('ix_lead_duplicate_candidates_duplicate_lead_id', 'lead_duplicate_candidates', ['duplicate_lead_id'], unique=False)
    op.create_index('ix_lead_duplicates_company_status', 'lead_duplicate_candidates', ['company_id', 'status'], unique=False)
    op.create_index('ix_lead_duplicates_confidence', 'lead_duplicate_candidates', ['company_id', 'confidence_tier'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_lead_duplicates_confidence', table_name='lead_duplicate_candidates')
    op.drop_index('ix_lead_duplicates_company_status', table_name='lead_duplicate_candidates')
    op.drop_index('ix_lead_duplicate_candidates_duplicate_lead_id', table_name='lead_duplicate_candidates')
    op.drop_index('ix_lead_duplicate_candidates_primary_lead_id', table_name='lead_duplicate_candidates')
    op.drop_index('ix_lead_duplicate_candidates_company_id', table_name='lead_duplicate_candidates')
    op.drop_table('lead_duplicate_candidates')

