from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database connection
engine = create_engine('sqlite:///chronos.db')
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define our Job table
class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    company = Column(String(200))
    location = Column(String(100))
    description = Column(Text, default='')
    job_url = Column(String(500), unique=True)
    source = Column(String(50))
    posted_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    is_applied = Column(Boolean, default=False)

# Create the database file
Base.metadata.create_all(engine)
print("✅ Database created successfully!")