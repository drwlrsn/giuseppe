""" Provides SQLAlchemy stuff """
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

try:
	DATABASE_URL = os.environ['DATABASE_URL']
except KeyError:
	DATABASE_URL = 'postgresql://giuseppe:Lc3XYHjWr6D4ER0IvhpMxH9lNMOlqF@localhost/giuseppe_db'
	
engine = create_engine(DATABASE_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
session = db_session

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import models
    Base.metadata.create_all(bind=engine)

