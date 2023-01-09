from pydantic import BaseModel, validator, validate_arguments
from typing import Optional, Union
from enum import Enum
from datetime import datetime
from uuid import UUID
from utils.mineminenomi import int_array_to_uuid


class FruitStatus(Enum):
    dropped = "DROPPED"
    inventory = "INVENTORY"
    in_use = "IN_USE"
    lost = "LOST"
    never_found = "NEVER_FOUND"


class HistoryEntry(BaseModel):
    uuid: Optional[Union[UUID, list[int, int, int, int]]] = None
    status: FruitStatus
    statusMessage: str
    date: datetime

    @validator("uuid", always=True)
    def get_uuid(cls, value, values) -> UUID:
        if isinstance(value, list):
            return int_array_to_uuid(value)
        return value


class DevilFruitEntry(BaseModel):
    fruit: str
    owner: Optional[Union[UUID, list[int, int, int, int]]] = None
    status: FruitStatus
    statusMessage: Optional[str]
    lastUpdate: datetime
    history: list[HistoryEntry]

    @validator("owner", always=True)
    def get_uuid(cls, value, values) -> UUID:
        if isinstance(value, list):
            return int_array_to_uuid(value)
        return value


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

    def __repr__(self):
        return f'<fruit="{self.format_name}" history={len(self.mod_data.history)}>'
