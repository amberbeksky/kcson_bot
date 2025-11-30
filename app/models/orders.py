from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    category = Column(String(100), nullable=False)  # "личный состав", "основная деятельность" и т.д.
    title = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)  # ссылка на файл в Google Drive
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("employees.id"))
