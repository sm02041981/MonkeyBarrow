from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship, declarative_base, validates
import datetime
from database import Base  # ✅ Use the imported Base, don’t redefine

# ----------------------------
# User (Employee) Table
# ----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)  # numeric PK
    employee_id = Column(String, unique=True, index=True)       # formatted ID
    mobile_number = Column(String, unique=True, index=True)
    role = Column(String, default="employee")  # "employee", "admin", etc.
    employment_status = Column(String, default="Active")  # "Active", "Suspended", "Not in Firm"
    totp_secret = Column(String, nullable=True)

    @validates("id")
    def generate_employee_id(self, key, value):
        self.employee_id = f"MB-EMP{value:03d}"
        return value

# ----------------------------
# Book Table
# ----------------------------
class Book(Base):
    __tablename__ = "books"

    mb_isbn13 = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    age_group = Column(String)
    category = Column(String)
    weight = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    mrp = Column(Float, nullable=True)
    image_fp_url = Column(String, nullable=True)  # Front page image (url only)
    last_updated_by = Column(String, nullable=True)

    image_other_url_1 = Column(String, nullable=True)
    image_other_url_2 = Column(String, nullable=True)
    image_other_url_3 = Column(String, nullable=True)

    bookitems = relationship("BookItem", back_populates="book")

# ----------------------------
# Toy Table
# ----------------------------
class Toy(Base):
    __tablename__ = "toys"

    mbcode = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    brand = Column(String)
    age_group = Column(String)
    category = Column(String)
    weight = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    mrp = Column(Float, nullable=True)
    last_updated_by = Column(String, nullable=True)

    image_other_url_1 = Column(String, nullable=True)
    image_other_url_2 = Column(String, nullable=True)
    image_other_url_3 = Column(String, nullable=True)

    toyitems = relationship("ToyItem", back_populates="toy")

# ----------------------------
# Premium Toy Table
# ----------------------------
class PremiumToy(Base):
    __tablename__ = "premiumtoys"

    mbcode = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    brand = Column(String)
    age_group = Column(String)
    category = Column(String)
    weight = Column(String, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    mrp = Column(Float, nullable=True)
    last_updated_by = Column(String, nullable=True)

    image_other_url_1 = Column(String, nullable=True)
    image_other_url_2 = Column(String, nullable=True)
    image_other_url_3 = Column(String, nullable=True)

    premiumtoyitems = relationship("PremiumToyItem", back_populates="premiumtoy")

# ----------------------------
# Order Table
# ----------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    shopify_order_id = Column(String, unique=True, index=True)
    customer_name = Column(String)
    customer_mobile = Column(String)
    customer_address = Column(String)
    customer_pincode = Column(String)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    estimated_delivery_date = Column(DateTime, nullable=True)
    order_status = Column(String, default="Ordered")

    bookitems = relationship("BookItem", back_populates="order")
    toyitems = relationship("ToyItem", back_populates="order")
    premiumtoyitems = relationship("PremiumToyItem", back_populates="order")

# ----------------------------
# Book Item Table
# ----------------------------
class BookItem(Base):
    __tablename__ = "book_items"

    serial_number = Column(String, primary_key=True, index=True)
    item_mb_isbn13 = Column(String, ForeignKey("books.mb_isbn13"))
    item_location = Column(String, default="MB-Parekh-Ground-Floor")
    date_of_purchase = Column(DateTime, default=datetime.datetime.utcnow)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # ✅ corrected type
    state = Column(String, default="Available")
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)

    book = relationship("Book", back_populates="bookitems")
    order = relationship("Order", back_populates="bookitems")
    bookhistory = relationship("BookStateHistory", back_populates="bookitem")

# ----------------------------
# Toy Item Table
# ----------------------------
class ToyItem(Base):
    __tablename__ = "toy_items"

    serial_number = Column(String, primary_key=True, index=True)
    item_mbcode = Column(String, ForeignKey("toys.mbcode"))
    item_location = Column(String, default="MB-Parekh-Ground-Floor")
    date_of_purchase = Column(DateTime, default=datetime.datetime.utcnow)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # ✅ corrected type
    state = Column(String, default="Available")
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)

    toy = relationship("Toy", back_populates="toyitems")
    order = relationship("Order", back_populates="toyitems")
    toyhistory = relationship("ToyStateHistory", back_populates="toyitems")

# ----------------------------
# Premium Toy Item Table
# ----------------------------
class PremiumToyItem(Base):
    __tablename__ = "premiumtoy_items"

    serial_number = Column(String, primary_key=True, index=True)
    item_mbcode = Column(String, ForeignKey("premiumtoys.mbcode"))
    item_location = Column(String, default="MB-Parekh-Ground-Floor")
    date_of_purchase = Column(DateTime, default=datetime.datetime.utcnow)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)  # ✅ corrected type
    state = Column(String, default="Available")
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)

    premiumtoy = relationship("PremiumToy", back_populates="premiumtoyitems")
    order = relationship("Order", back_populates="premiumtoyitems")
    premiumtoyhistory = relationship("PremiumToyStateHistory", back_populates="premiumtoyitems")

# ----------------------------
# Book State History
# ----------------------------
class BookStateHistory(Base):
    __tablename__ = "book_state_history"

    id = Column(Integer, primary_key=True, index=True)
    book_item_serial_number = Column(String, ForeignKey("book_items.serial_number"))
    state = Column(String)
    state_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    state_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)
    state_customer_mobile = Column(String, nullable=True)
    state_item_location = Column(String, default="MB-Parekh-Ground-Floor", nullable=True)

    bookitem = relationship("BookItem", back_populates="bookhistory")

# ----------------------------
# Toy State History
# ----------------------------
class ToyStateHistory(Base):
    __tablename__ = "toy_state_history"

    id = Column(Integer, primary_key=True, index=True)
    toy_item_serial_number = Column(String, ForeignKey("toy_items.serial_number"))
    state = Column(String)
    state_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    state_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)
    state_customer_mobile = Column(String, nullable=True)
    state_item_location = Column(String, default="MB-Parekh-Ground-Floor", nullable=True)

    toyitems = relationship("ToyItem", back_populates="toyhistory")

# ----------------------------
# Premium Toy State History
# ----------------------------
class PremiumToyStateHistory(Base):
    __tablename__ = "premiumtoy_state_history"

    id = Column(Integer, primary_key=True, index=True)
    premiumtoy_item_serial_number = Column(String, ForeignKey("premiumtoy_items.serial_number"))  # ✅ corrected FK
    state = Column(String)
    state_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    state_updated_by = Column(String, ForeignKey("users.employee_id"), nullable=True)
    state_customer_mobile = Column(String, nullable=True)
    state_item_location = Column(String, default="MB-Parekh-Ground-Floor", nullable=True)

    premiumtoyitems = relationship("PremiumToyItem", back_populates="premiumtoyhistory")
