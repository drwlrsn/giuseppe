"""Change Listing.numb_rooms to int.

Revision ID: 2e3f5ad82e0
Revises: 480e3ebe53a
Create Date: 2014-08-13 15:58:43.277551

"""

# revision identifiers, used by Alembic.
revision = '2e3f5ad82e0'
down_revision = '480e3ebe53a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE listing ALTER COLUMN numb_rooms TYPE int4 USING (trim(numb_rooms)::integer);')


def downgrade():
    op.alter_column('listing', sa.Column('numb_rooms', sa.String(10)))