from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional

class RegisterRequest(BaseModel):
    mobile_number: str

class RegisterResponse(BaseModel):
    message: str
    secret: str

class LoginRequest(BaseModel):
    mobile_number: str
    otp: str

class UserResponse(BaseModel):
    id: int
    mobile_number: str
    employee_id: str | None = None
    role: str

    model_config = ConfigDict(from_attributes=True)

class BookItemSchema(BaseModel):
    barcode: str
    serial_number: str
    book_id: int | None = None
    order_id: int | None = None
    state: str
    title: str | None = None
    author: str | None = None
    date_of_purchase: str | None = None
    weight: str | None = None
    age_group: str | None = None
    category: str | None = None
    last_updated_by: int | None = None
    last_updated: str | None = None

    @field_validator("date_of_purchase", "last_updated", mode="before")
    def datetime_to_string(cls, v):
        if hasattr(v, 'strftime'):
             return v.strftime("%Y-%m-%d %H:%M:%S")
        return v

    model_config = ConfigDict(from_attributes=True)

class StateUpdateRequest(BaseModel):
    barcode: str
    new_state: str
    agent_id: int

class HistorySchema(BaseModel):
    state: str
    timestamp: str
    updated_by: str | None = None

    model_config = ConfigDict(from_attributes=True)

class EmployeeRequest(BaseModel):
    mobile_number: str
    employee_id: str
    status: str

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
