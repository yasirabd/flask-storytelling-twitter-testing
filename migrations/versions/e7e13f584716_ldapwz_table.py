"""ldapwz table

Revision ID: e7e13f584716
Revises: 20c23f1ce2c4
Create Date: 2018-07-28 09:28:08.396043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7e13f584716'
down_revision = '20c23f1ce2c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ldapwz',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=200), nullable=True),
    sa.Column('topic', sa.Integer(), nullable=True),
    sa.Column('pwz', sa.String(length=200), nullable=True),
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['test_id'], ['test.id'], name=op.f('fk_ldapwz_test_id_test')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ldapwz'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ldapwz')
    # ### end Alembic commands ###
