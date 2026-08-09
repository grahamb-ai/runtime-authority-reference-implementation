"""add action and max_amount scope columns to delegation_grants

This is exactly the change that caused the "column delegation_grants.action
does not exist" error: the 'DelegationGrant' model gained two optional scope
fields, but 'create_tables()'  only creates missing tables. It never alters
an existing one, so a database created before this change is left out of
sync with the code until this migration is applied.

Revision ID: 0002_add_delegation_scope
Revises: 0001_baseline
Create Date: 2026-07-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_add_delegation_scope"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("delegation_grants", sa.Column("action", sa.String(), nullable=True))
    op.add_column("delegation_grants", sa.Column("max_amount", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("delegation_grants", "max_amount")
    op.drop_column("delegation_grants", "action")
