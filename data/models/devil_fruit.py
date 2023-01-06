from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from enum import Enum
from datetime import datetime


class FruitStatus(Enum):
    dropped = "DROPPED"
    inventory = "INVENTORY"
    in_use = "IN_USE"
    lost = "LOST"


class HistoryEntry(BaseModel):
    owner: Optional[UUID]
    status: FruitStatus
    statusMessage: str
    Date: datetime


class DevilFruitEntry(BaseModel):
    fruitKey: str
    owner: Optional[UUID]
    status: FruitStatus
    statusMessage: str
    Date: datetime
    history: list[HistoryEntry]


class DevilFruit(BaseModel):
    name: str
    format_name: str
    qualified_name: str
    rarity: str
    mod_data: DevilFruitEntry
