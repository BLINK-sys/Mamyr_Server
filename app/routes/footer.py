from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.footer import FooterSettings, FooterContact, FooterSchedule

router = APIRouter(prefix="/footer", tags=["footer"])


class ContactIn(BaseModel):
    id: int | None = None
    icon: str = ""
    text: str = ""
    order: int = 0
    iconColor: str | None = None
    textColor: str | None = None


class ScheduleIn(BaseModel):
    id: int | None = None
    text: str = ""
    order: int = 0
    textColor: str | None = None


class FooterIn(BaseModel):
    description: str = ""
    contacts: list[ContactIn] = []
    schedule: list[ScheduleIn] = []


@router.get("")
def get_footer(db: Session = Depends(get_db)):
    settings = db.query(FooterSettings).first()
    contacts = db.query(FooterContact).order_by(FooterContact.order).all()
    schedule = db.query(FooterSchedule).order_by(FooterSchedule.order).all()
    return {
        "description": settings.description if settings else "",
        "contacts": [{"id": c.id, "icon": c.icon, "text": c.text, "order": c.order, "iconColor": c.icon_color, "textColor": c.text_color} for c in contacts],
        "schedule": [{"id": s.id, "text": s.text, "order": s.order, "textColor": s.text_color} for s in schedule],
    }


@router.put("")
def update_footer(body: FooterIn, db: Session = Depends(get_db)):
    # Update description
    settings = db.query(FooterSettings).first()
    if not settings:
        settings = FooterSettings(description=body.description)
        db.add(settings)
    else:
        settings.description = body.description

    # Replace contacts
    db.query(FooterContact).delete()
    for c in body.contacts:
        db.add(FooterContact(icon=c.icon, text=c.text, order=c.order, icon_color=c.iconColor, text_color=c.textColor))

    # Replace schedule
    db.query(FooterSchedule).delete()
    for s in body.schedule:
        db.add(FooterSchedule(text=s.text, order=s.order, text_color=s.textColor))

    db.commit()
    return get_footer(db)
