from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.dish import Dish, DishAddon, DishLocation, DishStop, DishComboItem
from app.models.location import Location
from app.models.order import OrderItem

router = APIRouter(prefix="/dishes", tags=["dishes"])


class AddonIn(BaseModel):
    name: str
    price: int = 0


class DishIn(BaseModel):
    name: str
    desc: str = ""
    ingredients: str = ""
    price: int
    weight: str = ""
    image: str = ""
    active: bool = True
    isCombo: bool = False
    comboMin: int = 1
    comboMax: int = 4
    comboItemIds: list[int] = []
    categoryId: int
    locationIds: list[int] = []
    addons: list[AddonIn] = []


class StopIn(BaseModel):
    locationId: int


def dish_to_dict(d: Dish, db: Session) -> dict:
    stop_ids = [s.location_id for s in db.query(DishStop).filter(DishStop.dish_id == d.id).all()]
    combo_item_ids = [c.combo_dish_id for c in db.query(DishComboItem).filter(DishComboItem.dish_id == d.id).all()]
    return {
        "id": d.id,
        "name": d.name,
        "desc": d.desc,
        "ingredients": d.ingredients,
        "price": d.price,
        "weight": d.weight,
        "image": d.image,
        "active": d.active,
        "isCombo": d.is_combo,
        "comboMin": d.combo_min,
        "comboMax": d.combo_max,
        "comboItemIds": combo_item_ids,
        "categoryId": d.category_id,
        "locationIds": [loc.id for loc in d.locations],
        "stopLocationIds": stop_ids,
        "addons": [{"id": a.id, "name": a.name, "price": a.price} for a in d.addons],
    }


@router.get("")
def list_dishes(location_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Dish)
    if location_id:
        q = q.filter(Dish.locations.any(Location.id == location_id))
    rows = q.all()
    return [dish_to_dict(d, db) for d in rows]


@router.post("")
def create_dish(body: DishIn, db: Session = Depends(get_db)):
    dish = Dish(
        name=body.name, desc=body.desc, ingredients=body.ingredients,
        price=body.price, weight=body.weight, image=body.image,
        active=body.active, is_combo=body.isCombo, combo_min=body.comboMin,
        combo_max=body.comboMax, category_id=body.categoryId,
    )
    db.add(dish)
    db.flush()
    for a in body.addons:
        db.add(DishAddon(dish_id=dish.id, name=a.name, price=a.price))
    for lid in body.locationIds:
        db.add(DishLocation(dish_id=dish.id, location_id=lid))
    for cid in body.comboItemIds:
        db.add(DishComboItem(dish_id=dish.id, combo_dish_id=cid))
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish, db)


@router.put("/{dish_id}")
def update_dish(dish_id: int, body: DishIn, db: Session = Depends(get_db)):
    dish = db.query(Dish).get(dish_id)
    if not dish:
        return {"error": "not found"}
    dish.name = body.name
    dish.desc = body.desc
    dish.ingredients = body.ingredients
    dish.price = body.price
    dish.weight = body.weight
    dish.image = body.image
    dish.active = body.active
    dish.is_combo = body.isCombo
    dish.combo_min = body.comboMin
    dish.combo_max = body.comboMax
    dish.category_id = body.categoryId
    db.query(DishAddon).filter(DishAddon.dish_id == dish_id).delete()
    for a in body.addons:
        db.add(DishAddon(dish_id=dish_id, name=a.name, price=a.price))
    db.query(DishLocation).filter(DishLocation.dish_id == dish_id).delete()
    for lid in body.locationIds:
        db.add(DishLocation(dish_id=dish_id, location_id=lid))
    db.query(DishComboItem).filter(DishComboItem.dish_id == dish_id).delete()
    for cid in body.comboItemIds:
        db.add(DishComboItem(dish_id=dish_id, combo_dish_id=cid))
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish, db)


@router.delete("/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).get(dish_id)
    if dish:
        db.query(OrderItem).filter(OrderItem.dish_id == dish_id).delete()
        db.delete(dish)
        db.commit()
    return {"ok": True}


@router.post("/{dish_id}/stop")
def add_stop(dish_id: int, body: StopIn, db: Session = Depends(get_db)):
    existing = db.query(DishStop).filter(
        DishStop.dish_id == dish_id, DishStop.location_id == body.locationId
    ).first()
    if not existing:
        db.add(DishStop(dish_id=dish_id, location_id=body.locationId))
        db.commit()
    return {"ok": True}


@router.delete("/{dish_id}/stop/{location_id}")
def remove_stop(dish_id: int, location_id: int, db: Session = Depends(get_db)):
    db.query(DishStop).filter(
        DishStop.dish_id == dish_id, DishStop.location_id == location_id
    ).delete()
    db.commit()
    return {"ok": True}
