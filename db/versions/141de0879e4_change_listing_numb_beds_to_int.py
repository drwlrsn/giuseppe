"""Change Listing.numb_beds to int.

Revision ID: 141de0879e4
Revises: b40474fc90
Create Date: 2014-08-13 14:07:30.167306

"""

# revision identifiers, used by Alembic.
revision = '141de0879e4'
down_revision = 'b40474fc90'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE listing ALTER COLUMN numb_beds TYPE int4 USING (trim(numb_beds)::integer);')


def downgrade():
    op.alter_column('listing', sa.Column('numb_beds', sa.String(10)))
