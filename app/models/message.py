from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .declarative_base import Base
from sqlalchemy.sql import func

class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer(), primary_key=True)
    text = Column(String(1024), nullable=False)
    created_at = Column(DateTime(), default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=func.utc_timestamp())

    def __str__(self):
        return self.text
    
