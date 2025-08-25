from pydantic import BaseModel
from typing import Optional

class EventoBase(BaseModel):
    evento: str
    data: Optional[str] = None
    descricao: Optional[str] = None
    engajamento: Optional[int] = None
    status: Optional[str] = None
    origem: Optional[str] = None

class EventoCreate(EventoBase):
    pass

class EventoUpdate(BaseModel):
    evento: Optional[str] = None
    data: Optional[str] = None
    descricao: Optional[str] = None
    engajamento: Optional[int] = None
    status: Optional[str] = None
    origem: Optional[str] = None

class EventoInDB(EventoBase):
    id: int

    class Config:
        from_attributes = True