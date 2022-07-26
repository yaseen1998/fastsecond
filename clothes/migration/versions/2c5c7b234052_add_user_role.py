"""add user role

Revision ID: 2c5c7b234052
Revises: 00c20dd2ff59
Create Date: 2022-07-26 10:43:38.369502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c5c7b234052'
down_revision = '00c20dd2ff59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('clothes', sa.Column('role', sa.Enum('super_admin', 'admin', 'user', name='userrole'), server_default='user', nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('clothes', 'role')
    # ### end Alembic commands ###
