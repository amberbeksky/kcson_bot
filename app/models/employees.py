from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=True)
    fio = Column(String(255), nullable=False)
    role = Column(String(20), default="staff")  # staff / admin
    phone = Column(String(30))
    position = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
