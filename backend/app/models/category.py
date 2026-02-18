from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    slug = Column(String(100), unique=True, index=True)  # URL-friendly name
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_category_active", "is_active"),)

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"

    def to_dict(self):
        """Convert model to dictionary for caching"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
