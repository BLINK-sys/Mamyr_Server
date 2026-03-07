from sqlalchemy import Column, Integer, String
from app.database import Base


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String, default="")
    title = Column(String, default="")
    subtitle = Column(String, default="")
    order = Column(Integer, default=0)
