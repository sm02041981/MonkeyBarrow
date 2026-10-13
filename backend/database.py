"""
SM-MB-16-July-2026 - Database configuration with SQLAlchemy engine.
This file defines the database engine, session factory, and Base class.
Any change in database engine or URL must be updated here.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Example PostgreSQL URL format:
# postgresql://username:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://postgres:admin@localhost:5432/monkeybarrow_db"
)

# Create engine (Postgres doesn’t need connect_args like SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,        # checks connections before using them
    pool_size=10,              # number of connections in pool
    max_overflow=20,           # extra connections allowed
    echo=False                 # set True to log SQL queries for debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
