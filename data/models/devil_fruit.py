from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum
from datetime import datetime
from uuid import UUID
from utils.mineminenomi import int_array_to_uuid

class FruitStatus(Enum):
    dropped = "DROPPED"
    inventory = "INVENTORY"
    in_use = "IN_USE"
    lost = "LOST"


class HistoryEntry(BaseModel):
    uuid: Optional[list[int, int, int, int]] = None
    status: FruitStatus
    statusMessage: str
    date: datetime

    @validator("uuid", always=True)
    def get_uuid(cls, value, values) -> UUID:
        if value is None:
            return value
        return int_array_to_uuid(value)


class DevilFruitEntry(BaseModel):
    fruit: str
    owner: Optional[list[int, int, int, int]] = None
    status: FruitStatus
    statusMessage: Optional[str]
    lastUpdate: datetime
    history: list[HistoryEntry]

    @validator("owner", always=True)
    def get_uuid(cls, value, values) -> UUID:
        if value is None:
            return value
        return int_array_to_uuid(value)


class DevilFruitRarity(Enum):
    GOLDEN = "golden_box"
    IRON = "iron_box"
    WOODEN = "wooden_box"


class DevilFruit(BaseModel):
    name: str
    format_name: str
    qualified_name: str
    rarity: DevilFruitRarity
    mod_data: DevilFruitEntry
