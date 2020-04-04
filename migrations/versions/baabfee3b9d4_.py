"""empty message

Revision ID: baabfee3b9d4
Revises: c4bea4a57f07
Create Date: 2020-04-04 22:23:13.877555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'baabfee3b9d4'
down_revision = 'c4bea4a57f07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('users', sa.Column('adr', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'adr')
    op.drop_column('rooms', 'created_at')
    # ### end Alembic commands ###