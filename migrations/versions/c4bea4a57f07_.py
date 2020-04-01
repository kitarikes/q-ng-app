"""empty message

Revision ID: c4bea4a57f07
Revises: 4b1d932b8fb5
Create Date: 2020-04-02 00:04:24.481802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4bea4a57f07'
down_revision = '4b1d932b8fb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'users', ['username'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    # ### end Alembic commands ###
