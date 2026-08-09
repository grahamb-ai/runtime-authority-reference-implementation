"""baseline: rules, orders, delegation_grants (pre-scope)

Reflects the schema every existing deployment already has, since tables were
until now created ad hoc by SQLModel.metadata.create_all() (see
app/database.py) rather than through Alembic. This revision exists so
migration history has a known starting point to build on.

If you are setting up a BRAND NEW empty database, running alembic upgrade
head will create everything from scratch, including this baseline : no
manual step needed.

If your database already has these tables (i.e. you ran the app before
Alembic was introduced), do NOT let this revision try to re-create them.
Instead, tell Alembic your database is already at this point:

    alembic stamp 0001_baseline

Then 'alembic upgrade head' will only apply what comes after (see
0002_add_delegation_scope.py), with no manual SQL required.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-07-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# --- Alembic identifiers ---------------------------------------------------- #
revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rules",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("rule_type", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("attribute", sa.String(), nullable=False),
        sa.Column("operator", sa.String(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("source_document", sa.String(), nullable=False, server_default=""),
        sa.Column("source_excerpt", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target", sa.String(), nullable=False, server_default=""),
        sa.Column("requester_role", sa.String(), nullable=False, server_default=""),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False, server_default=""),
        sa.Column("authority_state", sa.String(), nullable=False, server_default=""),
        sa.Column("reason", sa.String(), nullable=False, server_default=""),
        sa.Column("required_action", sa.String(), nullable=True),
        sa.Column("checks", sa.JSON(), nullable=False),
        sa.Column("source_documents", sa.JSON(), nullable=False),
        sa.Column("sealed_at", sa.DateTime(timezone=True), nullable=False),
    )

    # Pre-scope shape: no 'action' / 'max_amount' columns yet (added in 0002).
    op.create_table(
        "delegation_grants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("requester_id", sa.String(), nullable=False),
        sa.Column("granted_by", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("delegation_grants")
    op.drop_table("orders")
    op.drop_table("rules")
