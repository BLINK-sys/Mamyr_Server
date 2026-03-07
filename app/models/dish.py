from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base


class DishLocation(Base):
    __tablename__ = "dish_locations"

    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True)


class DishAddon(Base):
    __tablename__ = "dish_addons"

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Integer, default=0)


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    desc = Column(String, default="")
    ingredients = Column(String, default="")
    price = Column(Integer, nullable=False)
    weight = Column(String, default="")
    image = Column(String, default="")
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    addons = relationship("DishAddon", cascade="all, delete-orphan", lazy="joined")
    locations = relationship("Location", secondary="dish_locations", lazy="joined")
