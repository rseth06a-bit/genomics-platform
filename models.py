#defines struct of database tables in python classes
#SQLalchemy handles SQL from python
from database import Base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey

#inherits from base in database.py so SQLAlchemy knows it's table
class Sample(Base):
    __tablename__="sample" #lowercase conventional?
    id = Column(Integer, primary_key=True, index=True)
        #primary_key says that id is like unique identifier column, i think that
        #no two rows can have same id  
        #index=True means we can use this for indexing to right row
    filename = Column(String)
    uploaded_at = Column(DateTime, server_default=func.now())
        #func.now(): tells Postgress to automatically create this when 
        #new row inserted, server_default means db sets value, python code
        # doesn't have to do it 

class Sequence(Base):
    __tablename__="sequence"
    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey("sample.id"))
        #basically matches id form sequence table to sample table 
        #makes sure that sample row isn't created without seuqence
        #or vice versa
    header = Column(String)
    raw_sequence = Column(Text) #Text and not string b/c sequence can be super long
    gc_content = Column(Float)
    seq_length = Column(Integer)
    kmer_json = Column(Text)
    label = Column(String)
    prediction = Column(String)
    confidence = Column(Float)