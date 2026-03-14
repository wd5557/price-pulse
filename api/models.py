"""
SQLAlchemy 模型定義
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class User(Base):
    """用戶模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 關聯
    products = relationship("Product", back_populates="user")

class Product(Base):
    """商品模型"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # amazon, ebay, walmart, generic
    product_id = Column(String(255), nullable=True)  # ASIN, SKU, or custom ID
    product_url = Column(String(1000), nullable=False)
    product_name = Column(String(500))
    image_url = Column(String(1000))
    target_price = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    lowest_price = Column(Numeric(10, 2))
    highest_price = Column(Numeric(10, 2))
    currency = Column(String(3), default="USD")
    
    is_active = Column(Boolean, default=True, index=True)
    check_interval = Column(Integer, default=3600)  # 檢查頻率（秒）
    last_checked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 關聯
    user = relationship("User", back_populates="products")
    price_histories = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="product")
    
    # 唯一約束
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', 'platform'),
    )

class PriceHistory(Base):
    """價格歷史模型"""
    __tablename__ = "price_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    is_available = Column(Boolean, default=True)
    seller_name = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 關聯
    product = relationship("Product", back_populates="price_histories")

class Notification(Base):
    """通知歷史模型"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    channel = Column(String(50), nullable=False)  # telegram, email, webhook
    status = Column(String(50))  # pending, sent, failed
    message = Column(Text)
    error = Column(Text)
    sent_at = DateTime(timezone=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    product = relationship("Product", back_populates="notifications")
