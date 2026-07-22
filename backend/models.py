"""
   SM-MB-16-July-20026 - this is a model file with SQLAlchemy models (User, BookItem, etc.).
   Basically here I am defining my database tables and their relationships. I am using SQLAlchemy ORM to define the models and their relationships. The models are defined as classes that inherit from the Base class, which is defined in the database.py file. Each class represents a table in the database, and each attribute of the class represents a column in the table. The relationships between the tables are defined using the relationship() function, which allows me to define one-to-many and many-to-one relationships between the tables.
   Any change in database tables will impact the models here, so I need to keep this file updated with any changes in the database schema.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
import datetime

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default="employee") # "employee" or "admin"
    status = Column(String, default="Active") # "Active", "Suspended", "Not in Firm"
    totp_secret = Column(String, nullable=True)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    age_group = Column(String)
    category = Column(String)
    weight = Column(String, nullable=True)
    description = Column(String, nullable=True)
    items = relationship("BookItem", back_populates="book")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    shopify_order_id = Column(String, unique=True, index=True)
    customer_name = Column(String)
    customer_mobile = Column(String)
    customer_address = Column(String)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    estimated_delivery_date = Column(DateTime, nullable=True)

    items = relationship("BookItem", back_populates="order")

class BookItem(Base):
    __tablename__ = "book_items"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True)
    serial_number = Column(String, unique=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    state = Column(String, default="Available") # Available, Ordered, Out for Delivery, Delivered, Returned, Sanitization, Damage/Repair
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    weight = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    category = Column(String, nullable=True)
    date_of_purchase = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    book = relationship("Book", back_populates="items")
    order = relationship("Order", back_populates="items")
    history = relationship("StateHistory", back_populates="item")

class StateHistory(Base):
    __tablename__ = "state_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("book_items.id"))
    state = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    item = relationship("BookItem", back_populates="history")
