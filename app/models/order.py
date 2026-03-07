from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class OrderItemAddon(Base):
    __tablename__ = "order_item_addons"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Integer, default=0)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    dish_name = Column(String, nullable=False)
    dish_price = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1)

    addons = relationship("OrderItemAddon", cascade="all, delete-orphan", lazy="joined")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="new")  # new, cooking, ready, delivered
    total = Column(Integer, default=0)
    cook_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    cook_name = Column(String, nullable=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("OrderItem", cascade="all, delete-orphan", lazy="joined")
