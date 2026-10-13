from pydantic import BaseModel, ConfigDict, field_validator, Field, validator
from typing import List, Optional, Any, Dict

# New Employee Register Request / Response - Schema
class RegisterRequest(BaseModel):
    mobile_number: str

class RegisterResponse(BaseModel):
    message: str
    secret: str

# Employee Login  Request - Schema
class LoginRequest(BaseModel):
    mobile_number: str
    otp: str

# Employee / Admin Login Response - Schema
class LoginResponse(BaseModel):
    access_token: str
    role: str
    model_config = ConfigDict(from_attributes=True)


# Employee Request / Response - Schema
class EmployeeRequest(BaseModel):
    mobile_number: str
    role: str
    employment_status: str
   
# Employee / Admin Login Response - Schema
class EmployeeResponse(BaseModel):
    mobile_number: str
    role: str
    employment_status: str
    model_config = ConfigDict(from_attributes=True, extra="ignore")


# This is used for add an BOOK inventory
class BookCreateRequest(BaseModel):
    mb_isbn13: str = Field(..., description="13-digit ISBN or barcode")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    age_group: str | None = Field(None, description="Target age group")
    category: str = Field(..., description="Book category")
    weight: str = Field(..., description="Weight as string, e.g. '500g'")
    description: str = Field(..., description="Book description")
    quantity: int = Field(..., ge=0, description="Quantity of items")
    mrp: float = Field(..., ge=0, description="Maximum retail price")
    image_fp_url: str = Field(..., description="Front image URL")
    last_updated_by: str | None = None
    
    
    
# This is used for add an ITEM inventory
class ItemCreateRequest(BaseModel):
    mbcode: str = Field(..., description="13-digit EAN or CODE")
    title: str = Field(..., description="Item title")
    brand: str = Field(..., description="Brand name")
    age_group: str | None = Field(None, description="Target age group")
    category: str = Field(..., description="Item category")
    weight: str = Field(..., description="Weight as string, e.g. '500g'")
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., ge=0, description="Quantity of items")
    mrp: float = Field(..., ge=0, description="Maximum retail price")
    last_updated_by: str | None = None
    inventory_type: str | None = None
    
    
    
    
# This is used for adding, fetching inventory    
class MBTLookupResponse(BaseModel):
    status: str  # 'EXISTS_IN_DB', 'FETCHED_FROM_GOOGLE', 'NOT_FOUND'
    message: str
    data: Optional[dict] = None

    
# This is used for fetch book details from backend and send to Flutter
class BookResponse(BaseModel):
    mb_isbn13: str
    title: str
    author: str
    age_group: str
    category: str
    weight: str
    description: str
    quantity: int | str   # can be number or string
    mrp: float | str      # can be number or string
    image_fp_url: str | None = None   # ✅ optional
    last_updated_by: str | None = None
   
   
class ItemResponse(BaseModel):
    mbcode: str
    title: str
    brand: str
    age_group: str
    category: str
    weight: str
    description: str
    quantity: int | str   # can be number or string
    mrp: float | str      # can be number or string
    last_updated_by: str | None = None
    inventory_type: str | None = None
   
    class Config:
        from_attributes = True 


class BookItemSchema(BaseModel):
    serial_number: str
    item_mb_isbn13: str
    item_location: str 
    date_of_purchase: str | None = None
    order_id: int | None = None
    state: str
    last_updated: str | None = None
    last_updated_by: str | None = None
    

    @field_validator("date_of_purchase", "last_updated", mode="before")
    def datetime_to_string(cls, v):
        if hasattr(v, 'strftime'):
             return v.strftime("%Y-%m-%d %H:%M:%S")
        return v

    model_config = ConfigDict(from_attributes=True, extra="ignore")

class StateUpdateRequest(BaseModel):
    serial_number: str
    employee_id: str | None = Field(None, description="employee_id")
    new_state: str | None = Field(None, description="To update Item new state")
    new_location: str | None = Field(None, description="To update warehouse location")
    order_id: str | None = Field(None, description="update order-id in case of manual order update required")
    
    
    class Config:
        from_attributes = True

class UpdateQuantityRequest(BaseModel):
    mb_isbn13: str
    quantity: int

class HistorySchema(BaseModel):
    book_item_id: str 
    state: str
    state_timestamp: str
    state_updated_by: str | None = None
    state_cust_mobile: str | None = None
    state_item_location: str | None = None
    
    model_config = ConfigDict(from_attributes=True, extra="ignore")


class QuantityUpdateRequest(BaseModel):
    mb_isbn13: str = Field(..., description="13-digit ISBN barcode")
    quantity: str = Field(..., description="Quantity to add")
    last_updated_by: str | None = None
    rack_code: Optional[str] = "001"

    class Config:
        from_attributes = True  # Pydantic v2 syntax 

class ShopifyCustomerInfo(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    default_address: Optional[dict] = None

class ShopifyLineItem(BaseModel):
    sku: str

class ShopifyOrderWebhookRequest(BaseModel):
    id: int
    name: str
    customer: Optional[ShopifyCustomerInfo] = None
    line_items: List[ShopifyLineItem]
