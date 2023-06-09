"""Create Transaction Table

Revision ID: 28e627756e66
Revises: 
Create Date: 2023-05-30 13:12:35.136374

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "28e627756e66"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tx_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.DECIMAL(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("is_credit", sa.Boolean(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transactions")
    # ### end Alembic commands ###
