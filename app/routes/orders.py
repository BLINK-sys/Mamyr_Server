from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.order import Order, OrderItem, OrderItemAddon

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderAddonIn(BaseModel):
    name: str
    price: int = 0


class OrderItemIn(BaseModel):
    dishId: int
    dishName: str
    dishPrice: int
    quantity: int = 1
    addons: list[OrderAddonIn] = []


class OrderIn(BaseModel):
    customerName: str
    customerPhone: str
    total: int
    items: list[OrderItemIn]


class StatusUpdate(BaseModel):
    status: str
    cookId: int | None = None
    cookName: str | None = None


def order_to_dict(o: Order) -> dict:
    return {
        "id": o.id,
        "status": o.status,
        "total": o.total,
        "cookId": o.cook_id,
        "cookName": o.cook_name,
        "customerName": o.customer_name,
        "customerPhone": o.customer_phone,
        "createdAt": o.created_at.isoformat() if o.created_at else None,
        "items": [
            {
                "dishId": item.dish_id,
                "dishName": item.dish_name,
                "dishPrice": item.dish_price,
                "quantity": item.quantity,
                "addons": [{"name": a.name, "price": a.price} for a in item.addons],
            }
            for item in o.items
        ],
    }


@router.get("")
def list_orders(db: Session = Depends(get_db)):
    rows = db.query(Order).order_by(Order.created_at.desc()).all()
    return [order_to_dict(o) for o in rows]


@router.post("")
def create_order(body: OrderIn, db: Session = Depends(get_db)):
    order = Order(
        customer_name=body.customerName,
        customer_phone=body.customerPhone,
        total=body.total,
    )
    db.add(order)
    db.flush()
    for item in body.items:
        oi = OrderItem(
            order_id=order.id, dish_id=item.dishId,
            dish_name=item.dishName, dish_price=item.dishPrice,
            quantity=item.quantity,
        )
        db.add(oi)
        db.flush()
        for addon in item.addons:
            db.add(OrderItemAddon(order_item_id=oi.id, name=addon.name, price=addon.price))
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        return {"error": "not found"}
    order.status = body.status
    if body.cookId:
        order.cook_id = body.cookId
    if body.cookName:
        order.cook_name = body.cookName
    db.commit()
    return order_to_dict(order)
