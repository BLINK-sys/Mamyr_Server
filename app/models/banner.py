from sqlalchemy import Column, Integer, String, Boolean, Float, JSON
from app.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="")
    active = Column(Boolean, default=True)
    image = Column(String, default="")
    overlay_opacity = Column(Float, default=0.5)
    order = Column(Integer, default=0)
    elements = Column(JSON, default=list)
    # Legacy fields kept for compatibility
    title = Column(String, default="")
    subtitle = Column(String, default="")
