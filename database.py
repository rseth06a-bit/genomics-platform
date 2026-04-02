#basically sets up everything needed to talk to PostgresSQL sb
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv() 
database_url = os.getenv('DATABASE_URL')

#takes databse url and connects to Postgress
engine = create_engine(database_url, echo=False) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    #creates session that doesn't automatically create changes, doesn't automatically
    #sync changes to the DB, and uses bind to tell engine which database to connect to
    #returns db
Base = declarative_base()
    #what database models will inherit later, kind of creating Base class
def get_db():
    db = SessionLocal() #opens a new db session, like connecting to the db
    try:
        yield db #FastAPI pauses get_db, gives db to whatever route needs it, only continues when route is done
    finally:
        db.close() #closes db even if there's errors

