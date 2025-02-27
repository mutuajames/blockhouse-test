"""
Database connection setup module.

This module handles the SQLAlchemy database connection configuration.
It provides session management and declares the base class for all models.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable or use SQLite as fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./orders.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Dependency function to get a database session.
    
    This function creates a new database session for each request
    and closes it when the request is finished.
    
    Yields:
        SQLAlchemy Session: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()