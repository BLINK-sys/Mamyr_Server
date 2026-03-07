from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.staff import Staff
from app.auth import hash_password

router = APIRouter(prefix="/staff", tags=["staff"])


class StaffIn(BaseModel):
    name: str
    email: str
    password: str
    role: str = "cook"
    locationId: int


def staff_to_dict(s: Staff) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "role": s.role,
        "locationId": s.location_id,
    }


@router.get("")
def list_staff(db: Session = Depends(get_db)):
    rows = db.query(Staff).all()
    return [staff_to_dict(s) for s in rows]


@router.post("")
def create_staff(body: StaffIn, db: Session = Depends(get_db)):
    s = Staff(
        name=body.name, email=body.email,
        password_hash=hash_password(body.password),
        role=body.role, location_id=body.locationId,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return staff_to_dict(s)


@router.put("/{staff_id}")
def update_staff(staff_id: int, body: StaffIn, db: Session = Depends(get_db)):
    s = db.query(Staff).get(staff_id)
    if not s:
        return {"error": "not found"}
    s.name = body.name
    s.email = body.email
    if body.password:
        s.password_hash = hash_password(body.password)
    s.role = body.role
    s.location_id = body.locationId
    db.commit()
    return staff_to_dict(s)


@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    s = db.query(Staff).get(staff_id)
    if s:
        db.delete(s)
        db.commit()
    return {"ok": True}
