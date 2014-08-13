"""Change Listing.list_price to float

Revision ID: b40474fc90
Revises: 47dcadbb6cc
Create Date: 2014-08-11 16:22:23.031455

"""

# revision identifiers, used by Alembic.
revision = 'b40474fc90'
down_revision = '47dcadbb6cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('ALTER TABLE listing ALTER COLUMN list_price TYPE float8 USING (trim(list_price)::float8);')


def downgrade():
    op.alter_column('listing', sa.Column('list_price', sa.String(10)))
