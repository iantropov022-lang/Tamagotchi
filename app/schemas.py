from pydantic import BaseModel
from datetime import datetime

class PetResponse(BaseModel):
    id: int
    name: str
    hunger: int
    happiness: int
    energy: int
    is_sleeping: bool
    last_updated: datetime

    class Config:
        from_attributes = True

class ActionResponse(BaseModel):
    message: str
    pet: PetResponse