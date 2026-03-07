from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="cook")  # owner, admin, cook, reception
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
