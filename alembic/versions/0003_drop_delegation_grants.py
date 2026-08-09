"""drop delegation_grants (delegation registry feature removed)

The server-side delegation registry ('DelegationGrant' model, the
'/api/v1/delegations' endpoints, and the resolution logic in
'routers/orders.py') was evaluated and then removed: granting a delegation
via Swagger/ '/docs' is no longer a supported capability. This migration
drops the now-unused table.

'delegation_validit' (in engines/authority.py) is unaffected as CODE
it still exists and is still exercised by the pure-engine tests that build an
OrderData directly  but it is dormant in the live API path, since nothing
populates OrderData.delegation_expires_at there any more.

Revision ID: 0003_drop_delegation_grants
Revises: 0002_add_delegation_scope
Create Date: 2026-07-10
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_drop_delegation_grants"
down_revision = "0002_add_delegation_scope"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("delegation_grants")


def downgrade() -> None:
    # Re-create the table exactly as it stood at the top of the previous
    # migration (0002), in case this removal is ever rolled back.
    op.create_table(
        "delegation_grants",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("requester_id", sa.String(), nullable=False),
        sa.Column("granted_by", sa.String(), nullable=True),
        sa.Column("action", sa.String(), nullable=True),
        sa.Column("max_amount", sa.Float(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
