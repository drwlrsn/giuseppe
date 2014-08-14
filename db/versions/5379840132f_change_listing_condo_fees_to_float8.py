"""Change Listing.condo_fees to float8.

Revision ID: 5379840132f
Revises: 2e3f5ad82e0
Create Date: 2014-08-14 11:52:17.035851

"""

# revision identifiers, used by Alembic.
revision = '5379840132f'
down_revision = '2e3f5ad82e0'

from alembic import op
import sqlalchemy as sa


def upgrade():
	statement = """
ALTER TABLE listing 
ALTER COLUMN condo_fees TYPE float8 
USING (
   CAST (
         CASE
         	WHEN condo_fees IS null THEN '0'
         	WHEN trim(condo_fees) = '' THEN '0'
         	ELSE condo_fees
         END
         AS float8
    )
)
"""
	op.execute(statement)


def downgrade():
    op.alter_column('listing', sa.Column('condo_fees', sa.String(100)))
