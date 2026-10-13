import datetime
from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

import models



#this is helper function to find location, floor, rack & box number
#based on inventory type & age category
def get_storage_config(inventory_type: str, age_category: str):
    """
    Returns: (location_code, floor_number, rack_number, box_capacity)
    """
    config_map = {
        # PAREKH BUILDING GROUND FLOOR
        ("Book", "0 to 3 Years"): (1, 0, "01", 30),
        ("Toy", "0 to 3 Years"): (1, 0, "02", 20),
        ("Book", "3 to 6 Years"): (1, 0, "03", 30),
        ("Toy", "3 to 6 Years"): (1, 0, "04", 20),
        
        # PAREKH BUILDING 1ST FLOOR
        ("Book", "6 to 9 Years"): (1, 1, "01", 30),
        ("Toy", "6 to 9 Years"): (1, 1, "02", 20),
        ("Book", "9 + Years"): (1, 1, "03", 30),
        ("Toy", "9 + Years"): (1, 1, "04", 20),
        
        # PREMIUM TOYS
        # PAREKH BUILDING GROUND FLOOR
        ("PremiumToy", None): (1, 0, "05", 15),
    }

    config = config_map.get((inventory_type, age_category)) or config_map.get(
        (inventory_type, None)
    )
    if not config:
        config = (1, 0, "99", 25)  # Fallback rule

    return config



#this is helper function to fetch isbn in case ot items 
# with code less than 13 digits
# its adds digits in prefix & suffix
def format_isbn13(isbn13: str, inventory_type: str) -> str:
    """
    Formats short ISBN strings to exactly 13 digits for Toy and PremiumToy types.
    """
    isbn_str = str(isbn13).strip()

    if inventory_type in ["Toy", "PremiumToy"]:
        if len(isbn_str) < 13:
            prefix = "201" if inventory_type == "Toy" else "301"
            isbn_str = prefix + isbn_str
            
            # Suffix with zeros if still less than 13 characters
            if len(isbn_str) < 13:
                isbn_str = isbn_str.ljust(13, "0")

    if len(isbn_str) != 13:
        raise ValueError(
            f"Invalid ISBN length ({len(isbn_str)}) for inventory type '{inventory_type}'. Must be 13 digits."
        )

    return isbn_str


#this is helper function to fetch database ORM model dynamically
def get_model_classes(inventory_type: str):
    """
    Maps inventory type string to the appropriate SQLAlchemy models.
    """
    model_map = {
        "Book": (models.BookItem, models.BookStateHistory),
        "Toy": (models.Toy, models.ToyStateHistory),
        "PremiumToy": (models.PremiumToy, models.PremiumToyStateHistory),
    }
    
    if inventory_type not in model_map:
        raise ValueError(f"Unsupported inventory type: {inventory_type}")
        
    return model_map[inventory_type]



#Main helper function called to add book, toy, premium toy to library
def create_product_items_and_history(
    db: Session,
    isbn13: str,
    quantity: int,
    employee_id: str,
    inventory_type: str,
    age_category: str,
):
    if quantity <= 0:
        return
    
    print(f"[quantity]: {quantity}")
    
    # 1. Format ISBN for non-book types
    if inventory_type in ["Toy", "PremiumToy"]:
        isbn13 = format_isbn13(isbn13, inventory_type)
        print(f"[isbn13 after calling format isbn function]: {isbn13}")
    
    
    print(f"[isbn13 for book, toy or premium toy]: {isbn13}")
    
    
    # Resolve ORM models dynamically
    ItemModel, HistoryModel = get_model_classes(inventory_type)
    print(f"[ItemModel]: {ItemModel}")
    print(f"[HistoryModel]: {HistoryModel}")
    

    # 2. Determine current highest sequence number for this specific item/ISBN
    existing_max_seq = (
        db.query(
            func.max(
                cast(func.substr(ItemModel.serial_number, 14, 2), Integer)
            )
        )
        .filter(ItemModel.item_mb_isbn13 == isbn13)
        .scalar()
    )
    print(f"[existing_max_seq]: {existing_max_seq}")

    start_seq = (int(existing_max_seq) + 1) if existing_max_seq is not None else 1
    now = datetime.datetime.now(datetime.timezone.utc)
    
    print(f"[start_seq]: {start_seq}")
    print(f"[now]: {now}")

    # 3. Resolve storage configuration
    location_code, floor_number, rack_number, box_capacity = get_storage_config(
        inventory_type, age_category
    )
    
    print(f"[location_code]: {location_code}")
    print(f"[floor_number]: {floor_number}")
    print(f"[rack_number]: {rack_number}")
    print(f"[rack_number]: {rack_number}")

    # 4. Count existing items in this rack (isolated to this model type to avoid mixing)
    existing_count = (
        db.query(ItemModel)
        .filter(func.substr(ItemModel.serial_number, 18, 2) == rack_number)
        .count()
    )
    print(f"[existing_count]: {existing_count}")

    # 5. Generate serialized items & state audit entries
    for i in range(quantity):
        seq_num = start_seq + i
        seq_str = f"{seq_num:02d}"

        # Calculate box rotation without exceeding rack box limits
        box_number = ((existing_count + i) // box_capacity) + 1
        if box_number > 14:
            raise ValueError(
                f"Rack {rack_number} capacity exceeded for {inventory_type} (max 12 boxes reached)."
            )

        box_str = f"{box_number:02d}"
        print(f"[box_str]: {box_str}")

        # 21-character structured serial:
        # [13 chars: ISBN] + [2 chars: Seq] + [1 char: Loc] + [1 char: Floor] + [2 chars: Rack] + [2 chars: Box]
        serial_number = f"{isbn13}{seq_str}{location_code}{floor_number}{rack_number}{box_str}"
        location_desc = f"Parekh Building, Floor: {floor_number}"
        
        print(f"[serial_number]: {serial_number}")
        print(f"[location_desc]: {location_desc}")

        # Insert item record
        item = ItemModel(
            serial_number=serial_number,
            item_mb_isbn13=isbn13,
            item_location=location_desc,
            date_of_purchase=now,
            order_id=None,
            state="Available",
            last_updated=now,
            last_updated_by=employee_id,
        )
        print(f"[item]: {item}")
        db.add(item)
        db.commit()
        db.refresh(item)
        db.flush()

        # Insert state history record
        history_entry = HistoryModel(
            book_item_serial_number=serial_number,
            state="Available",
            state_timestamp=now,
            state_updated_by=employee_id,
            state_customer_mobile=None,
            state_item_location=location_desc,
        )
        print(f"[history_entry]: {history_entry}")
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        db.flush()
        
    # Flush once after loop execution
    db.flush()