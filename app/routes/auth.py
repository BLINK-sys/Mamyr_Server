from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.staff import Staff
from app.auth import verify_password, create_token, require_auth

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.email == body.email).first()
    if not staff or not verify_password(body.password, staff.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(staff.id)
    return {
        "token": token,
        "user": {
            "id": staff.id,
            "name": staff.name,
            "email": staff.email,
            "role": staff.role,
            "locationId": staff.location_id,
        },
    }


@router.get("/me")
def me(user: Staff = Depends(require_auth)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "locationId": user.location_id,
    }
