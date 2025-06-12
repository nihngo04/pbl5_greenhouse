"""Add detection history and statistics tables

Revision ID: detection_history_001
Revises: 
Create Date: 2025-06-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'detection_history_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create detection_history table
    op.create_table('detection_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('original_image_path', sa.String(length=255), nullable=False),
        sa.Column('predicted_image_path', sa.String(length=255), nullable=True),
        sa.Column('detection_method', sa.String(length=50), nullable=False),
        sa.Column('camera_status', sa.String(length=20), nullable=True),
        sa.Column('ai_results_json', sa.Text(), nullable=False),
        sa.Column('total_leaves_detected', sa.Integer(), nullable=True),
        sa.Column('max_confidence', sa.Float(), nullable=True),
        sa.Column('disease_detected', sa.Boolean(), nullable=True),
        sa.Column('predicted_class', sa.String(length=100), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on timestamp for faster queries
    op.create_index('idx_detection_history_timestamp', 'detection_history', ['timestamp'])
    op.create_index('idx_detection_history_method', 'detection_history', ['detection_method'])
    op.create_index('idx_detection_history_disease', 'detection_history', ['disease_detected'])

    # Create detection_statistics table
    op.create_table('detection_statistics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_detections', sa.Integer(), nullable=True),
        sa.Column('automatic_detections', sa.Integer(), nullable=True),
        sa.Column('manual_detections', sa.Integer(), nullable=True),
        sa.Column('diseases_detected', sa.Integer(), nullable=True),
        sa.Column('healthy_detections', sa.Integer(), nullable=True),
        sa.Column('high_severity_count', sa.Integer(), nullable=True),
        sa.Column('medium_severity_count', sa.Integer(), nullable=True),
        sa.Column('low_severity_count', sa.Integer(), nullable=True),
        sa.Column('camera_online_count', sa.Integer(), nullable=True),
        sa.Column('camera_offline_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date')
    )
    
    # Create index on date for faster queries
    op.create_index('idx_detection_statistics_date', 'detection_statistics', ['date'])


def downgrade():
    # Drop tables and indexes
    op.drop_index('idx_detection_statistics_date', table_name='detection_statistics')
    op.drop_table('detection_statistics')
    
    op.drop_index('idx_detection_history_disease', table_name='detection_history')
    op.drop_index('idx_detection_history_method', table_name='detection_history')
    op.drop_index('idx_detection_history_timestamp', table_name='detection_history')
    op.drop_table('detection_history')
