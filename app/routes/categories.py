from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryIn(BaseModel):
    title: str
    order: int = 0
    active: bool = True


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Category).order_by(Category.order).all()
    return [{"id": r.id, "title": r.title, "order": r.order, "active": r.active} for r in rows]


@router.post("")
def create_category(body: CategoryIn, db: Session = Depends(get_db)):
    cat = Category(title=body.title, order=body.order, active=body.active)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return {"id": cat.id, "title": cat.title, "order": cat.order, "active": cat.active}


@router.put("/{cat_id}")
def update_category(cat_id: int, body: CategoryIn, db: Session = Depends(get_db)):
    cat = db.query(Category).get(cat_id)
    if not cat:
        return {"error": "not found"}
    cat.title = body.title
    cat.order = body.order
    cat.active = body.active
    db.commit()
    return {"id": cat.id, "title": cat.title, "order": cat.order, "active": cat.active}


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(Category).get(cat_id)
    if cat:
        db.delete(cat)
        db.commit()
    return {"ok": True}
