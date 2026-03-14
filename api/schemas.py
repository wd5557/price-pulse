"""
Pydantic schemas for API validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class PlatformEnum(str, Enum):
    amazon = "amazon"
    ebay = "ebay"
    walmart = "walmart"
    generic = "generic"

# 請求模型
class ProductCreate(BaseModel):
    url: str = Field(..., description="商品 URL")
    product_name: Optional[str] = Field(None, description="商品名稱（可選）")
    target_price: float = Field(..., gt=0, description="目標價格")
    platform: Optional[PlatformEnum] = Field(None, description="平台（可選，自動識別）")
    check_interval: Optional[int] = Field(3600, ge=300, description="檢查頻率（秒）")

class ProductUpdate(BaseModel):
    target_price: Optional[float] = None
    is_active: Optional[bool] = None

class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

# 響應模型
class ProductResponse(BaseModel):
    id: int
    platform: str
    product_url: str
    product_name: str
    target_price: Optional[float]
    current_price: Optional[float]
    currency: str
    is_active: bool
    created_at: str
    updated_at: str

class PriceCheckResponse(BaseModel):
    product_id: int
    status: str
    message: Optional[str] = None
    current_price: Optional[float] = None
    currency: Optional[str] = None

class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    currency: str
    timestamp: str
    is_available: bool

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    timezone: str
    is_active: bool
    created_at: str
