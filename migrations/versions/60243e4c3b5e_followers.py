"""followers

Revision ID: 60243e4c3b5e
Revises: e88cf2fda446
Create Date: 2022-10-07 23:06:40.179349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60243e4c3b5e'
down_revision = 'e88cf2fda446'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followers',
    sa.Column('follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('followers')
    # ### end Alembic commands ###
