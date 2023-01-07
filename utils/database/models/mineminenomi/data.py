from pydantic import BaseModel
from beanie import Document, Link, Indexed
from ..user import User
from uuid import UUID
from datetime import datetime
from typing import Optional
from data.models import Races, SubRaces, Factions, FightingStyles, DevilFruit


class PlayerStats(BaseModel):
    race: Optional[Races]
    sub_race: Optional[SubRaces]
    faction: Optional[Factions]
    fighting_style: Optional[FightingStyles]
    inventory: list[dict]
    belly: int
    bounty: int
    loyalty: int
    doriki: float
    busoshoku_haki: float
    kenboshoku_haki: float
    haoshoku_haki: bool
    haki_limit: float
    devil_fruits: list[DevilFruit]
    eaten_devil_fruits: list[DevilFruit]
    inventory_devil_fruits: list[DevilFruit]


class Player(Document):
    uuid: Indexed(UUID, unique=True)
    user: Optional[Link[User]] = None
    name: str
    last_update: datetime
    stats: PlayerStats
