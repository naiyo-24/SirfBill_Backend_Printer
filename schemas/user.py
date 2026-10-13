from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class UserAddress(BaseModel):
    label: str
    street: str
    city: str
    state: str
    pincode: str
    phone: Optional[str] = None
    is_default: bool = False

class UserBase(BaseModel):
    tenant_id: Optional[UUID] = None  # ADDED for multi-tenancy
    role: str
    phone: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    saved_addresses: Optional[Any] = None
    is_active: Optional[bool] = True
    location: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    role: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    saved_addresses: Optional[Any] = None
    is_active: Optional[bool] = None
    location: Optional[str] = None

class User(UserBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
