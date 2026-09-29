from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Барсик")

    hunger = Column(Integer, default=100)
    happiness = Column(Integer, default=100)
    energy = Column(Integer, default=100)

    is_sleeping = Column(Boolean, default=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())