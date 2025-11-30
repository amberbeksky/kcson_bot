from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    notify_before_days = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("employees.id"))
