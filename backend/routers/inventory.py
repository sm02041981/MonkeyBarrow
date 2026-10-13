"""
SM:16th August 2026 Updated: 4th September 2026
Backend for Inventory management, This program includes the following functionalities:
    It will have the following API endpoints:
    Case 1: Add New Inventory (book, toy, premiumtoy,stationery and workbooks, gift hampers, etc)
    Case 2: Update Inventory
"""
# -------------------------
# ADD INVENTORY
# Case:1 User may scan the ISBN number (13 digit code), if the book is present in database 
#           that may be a case where user would like to add the quantity of that book. Just update book quantity
#           Case:1.1  : Update quantity to Book Catalog table 
#           Case:1.2  : Add serial of those many books to book item table 
#           Case:1.3  : Add serial book status as 'Available' in state history table
#           Case:1.4  : Update quantity to Shopify product list

# Case:2 User may scan the ISBN number (13 digit code), if the book is not present in database, that means its a new 
#           book entry, so we will insert a book in catalogue table, book serial in book item table and book state as available 
#           state history table and add the product with available quantity to Shopify product list
#           Case:2.1  : Insert a new book to Book Catalog table 
#           Case:2.2  : Add serial of those many books to book item table 
#           Case:2.3  : Add serial book status as 'Available' in state history table
#           Case:2.4  : Add book and quantity to Shopify product list
# -------------------------
# -------------------------
#           ONCE THE BOOK IS ADDED AND QUANTITY IS INSERTED, PRINT LABELS EQUAL TO NEW QUANTITY ADDED         
#           LABEL SHOULD PRINT THE FOLLOWING DETAILS
#                   "MONKEYBARROW TECHNOLOGIES"
#           SERIAL No. : ISBN-nn
#           LOCATION:
# -------------------------
# -------------------------



# list of all import modules
import datetime
import os
import requests
from fastapi import FastAPI, UploadFile, File, Form
import json
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from routers.gcsuploader import upload_multiple_to_gcs
import models
import schemas
from database import SessionLocal
from fastapi import Request
from .shopify_api import create_product, update_quantity as shopify_update_quantity
from .create_book_product import create_product_items_and_history
from .book_detail_api import get_book_details

#from .thermal_print_module  import _print_label

from schemas import MBTLookupResponse

#from .gcs_uploader import upload_to_gcs

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# Logout Endpoint
# -------------------------

@router.post("/logout")
def logout(response: Response):
    # If using cookies:
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}

# -------------------------
# SEARCH / GET INVENTORY info from Library
# simply search if the book is in database or not
# -------------------------
  
@router.get("/{isbn}", response_model=schemas.MBTLookupResponse)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    print(f"I am in isbn api with ISBN {isbn}")
    book = db.query(models.Book).filter(models.Book.mb_isbn13 == isbn).first()
    
    # ==========================================
    # CASE 1: Found in MonkeyBarrow DB
    # ==========================================  
    
    if book:
        # This is used for adding, fetching inventory    
        print(f"✅ Book found in MonkeyBarrow Database for ISBN {isbn}")
        return MBTLookupResponse(
            status="EXISTS_IN_DB",
            message="Product already exists in MonkeyBarrow database.",
            data={
                "mb_isbn13": book.mb_isbn13,
                "title": book.title,
                "author": book.author,
                "age_group": book.age_group,
                "category": book.category,
                "weight": book.weight,
                "description": book.description,
                "quantity": book.quantity,
                "mrp": book.mrp,
                "image_fp_url": book.image_fp_url,
                "last_updated_by": book.last_updated_by,
            },
        )
    
   # --- Case 2: Not in DB -> Query Google Books API ---
    # ==========================================
    print(f"Book not in DB, querying Google Books API for ISBN: {isbn}")

    try:
        book_response = get_book_details(isbn)
        if book_response:
            return MBTLookupResponse(
                status="FETCHED_FROM_EXTERNAL",
                message="Book metadata fetched from external sources.",
                data={
                    "mb_isbn13": isbn,
                    "title": book_response.get("title", ""),
                    "author": book_response.get("author", ""),
                    "category": (
                        book_response.get("categories")[0]
                        if book_response.get("categories")
                        else ""
                    ),
                    "weight": book_response.get("weight", "400"),
                    "description": book_response.get("description", ""),
                    "publisher": book_response.get("publisher", ""),
                    "publishedDate": book_response.get("publishedDate", ""),
                    "image_fp_url": book_response.get("thumbnail", ""),
                },
            )
    except requests.RequestException as e:
        print(f"External API request failed: {e}")
        raise HTTPException(status_code=502, detail="External book metadata service unavailable.")

        # --- Case 3: Not in DB & Not in external sources ---
    print(f"❌ Book not found anywhere for ISBN {isbn}")
    return MBTLookupResponse(
            status="NOT_FOUND",
            message="Book not found in MonkeyBarrow DB or external sources. Please enter details manually.",
            data={"mb_isbn13": isbn}
    )
    
# -------------------------
# CASE 1: UPDATE QUANTITY to Library
#  // updateQuantity helper function which does following tasks
#  // 1. In Json it receives: isbn, additional quantity, last updated by & rack code
#  // 2. As the book is already present in book table, 
#  // 2.a it create serial book entries into database
#  // 3. Print the serial bar code to be pasted on the book
#  // 4. update the new available book quantity to shopify website
# -------------------------
@router.post("/updatequantity", response_model=schemas.BookResponse)
def update_quantity(request: schemas.QuantityUpdateRequest, db: Session = Depends(get_db)):
    print("📥 Incoming update quantity request:", request.model_dump())

    # 1. Parse and validate incoming quantity delta
    try:
        qty_to_add = int(request.quantity)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Quantity must be a valid integer."
        )

    if qty_to_add <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity to add must be greater than zero."
        )
    
    
    book = db.query(models.Book).filter(models.Book.mb_isbn13 == request.mb_isbn13).first()
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ISBN {request.mb_isbn13} not found in catalog."
        )
        
    try:
        #Update total quantity in Book Catalog
        employee_id = getattr(request, 'last_updated_by', None) or getattr(book, 'last_updated_by', 'SYSTEM')
        age_group = getattr(request, 'age_group', None) or book.age_group or ""
        
        # Generate 21-digit serial items and state history records
        create_product_items_and_history(
                    db=db,
                    isbn13=request.mb_isbn13,
                    quantity=qty_to_add,
                    employee_id=employee_id,
                    inventory_type='Book',
                    age_category=age_group
        )
        
        # 5. Update and assign the new total quantity to the Book catalog
        employee_id = request.last_updated_by if request.last_updated_by is not None else ""
        
        current_qty = int(book.quantity) if book.quantity is not None else 0
        qty_to_add = int(request.quantity) if request.quantity is not None else 0
        
        print(f"✅ Quantity {current_qty} units for qty_to_add={qty_to_add}")
        new_total_qty = current_qty + qty_to_add
        print(f"✅ new_total_qty {new_total_qty}")
        
        book.quantity = int(new_total_qty)
        print(f"✅ new book qyuanity should be {book.quantity}")
        
        if hasattr(book, 'last_updated_by'):
            book.last_updated_by = employee_id
        
        # Retry Shopify update
        shopify_update_quantity(book.mb_isbn13, new_total_qty)

        db.commit()
        db.refresh(book)
        
        print(f"✅ Successfully added {qty_to_add} units for ISBN={book.mb_isbn13}. New total: {book.quantity}")
        return book

    except Exception as e:
        db.rollback()
        print(f"❌ Error updating quantity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# -------------------------
# CASE 2: ADD NEW BOOK  to Library
#  // addbook helper function which does following tasks
#  // 1. Insert a book into database, create serial book entries into database
#  // 2. Print the serial bar code to be pasted on the book
#  // 3. upload the image to google cloud and share the public url for shopify
#  // 4. upload the book to shopify website
# -------------------------
@router.post("/addbook", response_model=schemas.BookResponse)
async def add_inventory(
    #request: schemas.BookCreateRequest = Depends(),
    # Accept the Pydantic model data as a single JSON string via Form
    #book_data_str: str = Form(...),
    book_data_str: str = Form(...),
    files: List[UploadFile] = File(...),      
    db: Session = Depends(get_db)
):
        
    # Parse the incoming JSON string into your Pydantic schema
    try:
        book_dict = json.loads(book_data_str)
        print(f"📥 Incoming book_dict book request: {book_dict}")    
        request = schemas.BookCreateRequest(**book_dict)
        print(f"📥 Incoming book_dict book request: {request}")    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON in book_data_str")
        
    print("📥 Incoming add book request:", request.model_dump())
    
    existing = db.query(models.Book).filter(models.Book.mb_isbn13 == request.mb_isbn13).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Book with ISBN {request.mb_isbn13} already exists. Use /updatequantity instead."
        )    
    
    try:
        
        # Upload images to GCS
        file_data = [(f.file, f.filename) for f in files]
        image_urls = upload_multiple_to_gcs(file_data, request.mb_isbn13, "bookinventory")
        
        # Merge metadata + image URLs
        book_data = request.model_dump()
        book_data["image_other_url_1"] = image_urls[0] if len(image_urls) > 2 else None
        book_data["image_other_url_2"] = image_urls[1] if len(image_urls) > 3 else None
        book_data["image_other_url_3"] = image_urls[2] if len(image_urls) > 4 else None
        
        # Insert new book into Book Catalog table
        book = models.Book(**book_data)
        db.add(book)
        db.commit()
        db.refresh(book)
        db.flush()
        
        print(f"📥 Book Data:{db}")
        print(f"📥 Book Data:{request.mb_isbn13,}")
        print(f"📥 Book Data:{int(book_data.get('quantity', 0) or 0)}")
        print(f"📥 Book Data:{book_data.get('last_updated_by')}")
        print(f"📥 Book Data:Book")
        print(f"📥 Book Data:{book_data.get('age_group')}")
             
        # Generate 20-digit serial items & state history records
        create_product_items_and_history(
            db=db,
            isbn13=request.mb_isbn13,
            quantity=int(book_data.get("quantity", 0) or 0),
            employee_id=book_data.get("last_updated_by"),
            inventory_type='Book',
            age_category=book_data.get("age_group")
        )
        print(f"Came back successfully from create product")
        
        # Retry Shopify create
        create_product(
            book_data["mb_isbn13"],
            book_data["title"],
            book_data["author"],
            book_data.get("age_group"),
            book_data["category"],
            book_data["weight"],
            book_data["description"],
            book_data["mrp"],
            book_data.get("image_fp_url"),
            book_data.get("image_other_url_1"),
            book_data.get("image_other_url_2"),
            book_data.get("image_other_url_3"),
            book_data.get("last_updated_by"),
            int(book_data.get("quantity",0) or 0),
            inventory_type='Book',
        )
        return book

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding new book: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # -------------------------
# CASE 2: ADD NON BOOK ITEM to Library
#  // additem helper function which does following tasks
#  // 1. Insert a item into database, create serial item entries into database
#  // 2. Print the serial bar code to be pasted on the item
#  // 3. upload the image to google cloud and share the public url for shopify
#  // 4. upload the book to shopify website
# -------------------------
@router.post("/additem", response_model=schemas.ItemResponse)
async def add_inventory(
    #request: schemas.BookCreateRequest = Depends(),
    # Accept the Pydantic model data as a single JSON string via Form
    #book_data_str: str = Form(...),
    item_data_str: str = Form(...),
    files: List[UploadFile] = File(...),      
    db: Session = Depends(get_db)
):
    # Parse the incoming JSON string into your Pydantic schema
    try:
        item_dict = json.loads(item_data_str)
        request = schemas.ItemCreateRequest(**item_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON in book_data_str")
        
    print("📥 Incoming add item request:", request.model_dump())
    
    existing = db.query(models.Book).filter(models.Book.mb_isbn13 == request.mb_isbn13).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Book with ISBN {request.mb_isbn13} already exists. Use /updatequantity instead."
        )    
    
    try:
        
        # Upload images to GCS
        file_data = [(f.file, f.filename) for f in files]
        image_urls = upload_multiple_to_gcs(file_data, request.mb_isbn13, request.inventory_type)
        
        # Merge metadata + image URLs
        item_data = request.model_dump()
        item_data["image_other_url_1"] = image_urls[0] if len(image_urls) > 2 else None
        item_data["image_other_url_2"] = image_urls[1] if len(image_urls) > 3 else None
        item_data["image_other_url_3"] = image_urls[2] if len(image_urls) > 4 else None
        
        item1 = models.Toy(**item_data)
        # Insert new Toy into Toy Catalog table
        if request.inventory_type == "Toy":
            item1 = models.Toy(**item_data)
            db.add(item1)
            db.commit()
            db.refresh(item1)
            db.flush()

        elif request.inventory_type == "PremiumToy":
            item1 = models.PremiumToy(**item_data)
            db.add(item1)
            db.commit()
            db.refresh(item1)
            db.flush()

        else:
            # Do nothing
            pass
    

        # Generate 21-digit serial items & state history records
        #initial_qty = int(book_data.quantity or 0)
        
        create_product_items_and_history(
            db=db,
            isbn13=item_data["mbcode"],
            quantity=int(item_data.get("quantity", 0) or 0),
            employee_id=item_data.get("last_updated_by"),
            inventory_type=item_data.get("inventory_type"),
            age_category=item_data.get("age_group")
        )
        
        
        # Retry Shopify create
        create_product(
            item_data["mbcode"],
            item_data["title"],
            item_data["brand"],
            item_data.get("age_group"),
            item_data["category"],
            item_data["weight"],
            item_data["description"],
            item_data["mrp"],
            "",
            item_data.get("image_other_url_1"),
            item_data.get("image_other_url_2"),
            item_data.get("image_other_url_3"),
            item_data.get("last_updated_by"),
            int(item_data.get("quantity",0) or 0),            
            item_data.get("inventory_type"),
        )
        
        # Insert new Toy into Toy Catalog table
        if request.inventory_type == "Toy":
            db.commit()
            db.refresh(item1)
                
        elif request.inventory_type == "PremiumToy":
            db.commit()
            db.refresh(item1)
                        
        else:
            # Do nothing
            pass
   
        #print(f"✅ New book & {initial_qty} items inserted with ISBN={book.mb_isbn13}")
        return item1

    except Exception as e:
        db.rollback()
        print(f"❌ Error adding new book: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")