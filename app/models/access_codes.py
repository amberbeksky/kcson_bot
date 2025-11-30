from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class AccessCode(Base):
    __tablename__ = "access_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False)
    role = Column(String(20), default="staff")  # staff / admin
    used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
