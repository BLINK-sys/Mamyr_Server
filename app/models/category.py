from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    order = Column(Integer, default=0)
    active = Column(Boolean, default=True)
