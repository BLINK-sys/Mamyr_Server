from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.dish import Dish, DishAddon, DishLocation
from app.models.location import Location

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
    categoryId: int
    locationIds: list[int] = []
    addons: list[AddonIn] = []


def dish_to_dict(d: Dish) -> dict:
    return {
        "id": d.id,
        "name": d.name,
        "desc": d.desc,
        "ingredients": d.ingredients,
        "price": d.price,
        "weight": d.weight,
        "image": d.image,
        "categoryId": d.category_id,
        "locationIds": [loc.id for loc in d.locations],
        "addons": [{"id": a.id, "name": a.name, "price": a.price} for a in d.addons],
    }


@router.get("")
def list_dishes(location_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Dish)
    if location_id:
        q = q.filter(Dish.locations.any(Location.id == location_id))
    rows = q.all()
    return [dish_to_dict(d) for d in rows]


@router.post("")
def create_dish(body: DishIn, db: Session = Depends(get_db)):
    dish = Dish(
        name=body.name, desc=body.desc, ingredients=body.ingredients,
        price=body.price, weight=body.weight, image=body.image,
        category_id=body.categoryId,
    )
    db.add(dish)
    db.flush()
    for a in body.addons:
        db.add(DishAddon(dish_id=dish.id, name=a.name, price=a.price))
    for lid in body.locationIds:
        db.add(DishLocation(dish_id=dish.id, location_id=lid))
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish)


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
    dish.category_id = body.categoryId
    # Update addons
    db.query(DishAddon).filter(DishAddon.dish_id == dish_id).delete()
    for a in body.addons:
        db.add(DishAddon(dish_id=dish_id, name=a.name, price=a.price))
    # Update locations
    db.query(DishLocation).filter(DishLocation.dish_id == dish_id).delete()
    for lid in body.locationIds:
        db.add(DishLocation(dish_id=dish_id, location_id=lid))
    db.commit()
    db.refresh(dish)
    return dish_to_dict(dish)


@router.delete("/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).get(dish_id)
    if dish:
        db.delete(dish)
        db.commit()
    return {"ok": True}
