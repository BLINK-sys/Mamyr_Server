from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from pydantic import BaseModel
from typing import Any, List
from app.database import get_db
from app.models.banner import Banner

router = APIRouter(prefix="/banners", tags=["banners"])


class BannerIn(BaseModel):
    name: str = ""
    active: bool = True
    image: str = ""
    overlay_opacity: float = 0.5
    order: int = 0
    elements: List[Any] = []


def banner_to_dict(b: Banner):
    return {
        "id": b.id,
        "name": b.name or b.title or "",
        "active": b.active if b.active is not None else True,
        "image": b.image or "",
        "overlay_opacity": b.overlay_opacity if b.overlay_opacity is not None else 0.5,
        "order": b.order,
        "elements": b.elements or [],
        "title": b.title or "",
        "subtitle": b.subtitle or "",
    }


@router.get("")
def list_banners(db: Session = Depends(get_db)):
    rows = db.query(Banner).order_by(Banner.order).all()
    return [banner_to_dict(r) for r in rows]


@router.post("")
def create_banner(body: BannerIn, db: Session = Depends(get_db)):
    b = Banner(
        name=body.name, active=body.active, image=body.image,
        overlay_opacity=body.overlay_opacity, order=body.order, elements=body.elements,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return banner_to_dict(b)


@router.put("/{banner_id}")
def update_banner(banner_id: int, body: BannerIn, db: Session = Depends(get_db)):
    b = db.query(Banner).get(banner_id)
    if not b:
        return {"error": "not found"}
    b.name = body.name
    b.active = body.active
    b.image = body.image
    b.overlay_opacity = body.overlay_opacity
    b.order = body.order
    b.elements = body.elements
    flag_modified(b, "elements")
    db.commit()
    return banner_to_dict(b)


@router.patch("/{banner_id}/toggle")
def toggle_banner(banner_id: int, db: Session = Depends(get_db)):
    b = db.query(Banner).get(banner_id)
    if not b:
        return {"error": "not found"}
    b.active = not (b.active if b.active is not None else True)
    db.commit()
    return banner_to_dict(b)


@router.delete("/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db)):
    b = db.query(Banner).get(banner_id)
    if b:
        db.delete(b)
        db.commit()
    return {"ok": True}
