from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.location import Location

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationIn(BaseModel):
    name: str
    address: str = ""


@router.get("")
def list_locations(db: Session = Depends(get_db)):
    rows = db.query(Location).all()
    return [{"id": r.id, "name": r.name, "address": r.address} for r in rows]


@router.post("")
def create_location(body: LocationIn, db: Session = Depends(get_db)):
    loc = Location(name=body.name, address=body.address)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return {"id": loc.id, "name": loc.name, "address": loc.address}


@router.put("/{loc_id}")
def update_location(loc_id: int, body: LocationIn, db: Session = Depends(get_db)):
    loc = db.query(Location).get(loc_id)
    if not loc:
        return {"error": "not found"}
    loc.name = body.name
    loc.address = body.address
    db.commit()
    return {"id": loc.id, "name": loc.name, "address": loc.address}


@router.delete("/{loc_id}")
def delete_location(loc_id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).get(loc_id)
    if loc:
        db.delete(loc)
        db.commit()
    return {"ok": True}
