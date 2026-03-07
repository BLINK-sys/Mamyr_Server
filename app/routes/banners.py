from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.banner import Banner

router = APIRouter(prefix="/banners", tags=["banners"])


class BannerIn(BaseModel):
    image: str = ""
    title: str = ""
    subtitle: str = ""
    order: int = 0


@router.get("")
def list_banners(db: Session = Depends(get_db)):
    rows = db.query(Banner).order_by(Banner.order).all()
    return [{"id": r.id, "image": r.image, "title": r.title, "subtitle": r.subtitle, "order": r.order} for r in rows]


@router.post("")
def create_banner(body: BannerIn, db: Session = Depends(get_db)):
    b = Banner(image=body.image, title=body.title, subtitle=body.subtitle, order=body.order)
    db.add(b)
    db.commit()
    db.refresh(b)
    return {"id": b.id, "image": b.image, "title": b.title, "subtitle": b.subtitle, "order": b.order}


@router.put("/{banner_id}")
def update_banner(banner_id: int, body: BannerIn, db: Session = Depends(get_db)):
    b = db.query(Banner).get(banner_id)
    if not b:
        return {"error": "not found"}
    b.image = body.image
    b.title = body.title
    b.subtitle = body.subtitle
    b.order = body.order
    db.commit()
    return {"id": b.id, "image": b.image, "title": b.title, "subtitle": b.subtitle, "order": b.order}


@router.delete("/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    b = db.query(Banner).get(banner_id)
    if b:
        db.delete(b)
        db.commit()
    return {"ok": True}
