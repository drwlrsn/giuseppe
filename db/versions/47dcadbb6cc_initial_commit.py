"""Initial commit

Revision ID: 47dcadbb6cc
Revises: None
Create Date: 2014-08-11 16:17:17.673678

"""

# revision identifiers, used by Alembic.
revision = '47dcadbb6cc'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('school', 'location')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_index('idx_transit_stop_location', 'transit_stop', ['location'], unique=False)
    op.create_index('idx_super_market_location', 'super_market', ['location'], unique=False)
    op.create_index('idx_school_location', 'school', ['location'], unique=False)
    op.create_index('idx_school_geom', 'school', ['geom'], unique=False)
    op.add_column('school', sa.Column('location', sa.Geometry(geometry_type='POINT', srid=4326), autoincrement=False, nullable=True))
    op.create_index('idx_place_of_worship_location', 'place_of_worship', ['location'], unique=False)
    op.create_index('listing_gix', 'listing', ['location'], unique=False)
    op.create_index('idx_listing_location', 'listing', ['location'], unique=False)
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    ### end Alembic commands ###
