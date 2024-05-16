from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .declarative_base import Base
from sqlalchemy.sql import func

class Contact(Base):
    __tablename__ = 'contact'

    id = Column(Integer(), primary_key=True)
    whatsapp_id = Column(String(1024), nullable=False)
    whatsapp_name = Column(String(1024), nullable=False)
    name = Column(String(1024))
    description = Column(String(1024))
    category = Column(String(1024))
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=func.utc_timestamp())

    def __str__(self):
        return self.name
    
