from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class FooterContact(Base):
    __tablename__ = "footer_contacts"

    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String, default="")
    text = Column(String, default="")
    order = Column(Integer, default=0)
    icon_color = Column(String, nullable=True)
    text_color = Column(String, nullable=True)


class FooterSchedule(Base):
    __tablename__ = "footer_schedule"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, default="")
    order = Column(Integer, default=0)
    text_color = Column(String, nullable=True)


class FooterSettings(Base):
    __tablename__ = "footer_settings"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, default="")
