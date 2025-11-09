from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, func, event
from sqlalchemy.orm import declarative_base, declared_attr
from app.core.database import Base


class AuditMixin:
    """Mixin to add audit columns to all models"""
    
    @declared_attr
    def date_added(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @declared_attr
    def date_updated(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def added_by(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)


class BaseModel(Base, AuditMixin):
    """Base model for all entities with audit columns"""
    __abstract__ = True
