"""Add disease detection tables

Revision ID: 1234567890ab
Revises: 
Create Date: 2025-06-11 10:20:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '1234567890ab'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create disease_detections table
    op.create_table('disease_detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('original_image', sa.String(), nullable=False),
        sa.Column('predicted_image', sa.String(), nullable=True),
        sa.Column('results', sqlite.JSON(), nullable=True),
        sa.Column('max_confidence', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disease_detections_id'), 'disease_detections', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_disease_detections_id'), table_name='disease_detections')
    op.drop_table('disease_detections')
