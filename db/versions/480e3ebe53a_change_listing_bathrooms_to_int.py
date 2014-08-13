"""Change Listing.bathrooms to int.

Revision ID: 480e3ebe53a
Revises: 141de0879e4
Create Date: 2014-08-13 15:55:39.189167

"""

# revision identifiers, used by Alembic.
revision = '480e3ebe53a'
down_revision = '141de0879e4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE listing ALTER COLUMN bathrooms TYPE int4 USING (trim(bathrooms)::integer);')


def downgrade():
    op.alter_column('listing', sa.Column('bathrooms', sa.String(10)))