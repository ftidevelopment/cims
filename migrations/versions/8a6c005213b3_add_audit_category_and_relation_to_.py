"""Add audit category master

Revision ID: 8a6c005213b3
Revises: a9fe446bd148
Create Date: 2026-10-03 21:34:13.725794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a6c005213b3'
down_revision = 'a9fe446bd148'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # Create Audit Category master table
    # ============================================================
    op.create_table(
        'audit_categories',
        sa.Column(
            'audit_category_code',
            sa.String(length=10),
            nullable=False
        ),
        sa.Column(
            'audit_category_name',
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            'description',
            sa.Text(),
            nullable=True
        ),
        sa.Column(
            'id',
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False
        ),
        sa.Column(
            'created_by',
            sa.String(length=50),
            nullable=True
        ),
        sa.Column(
            'updated_by',
            sa.String(length=50),
            nullable=True
        ),
        sa.Column(
            'is_active',
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            'version',
            sa.Integer(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('audit_category_code'),
        sa.UniqueConstraint('audit_category_name')
    )


def downgrade():
    # ============================================================
    # Remove Audit Category master table
    # ============================================================
    op.drop_table('audit_categories')