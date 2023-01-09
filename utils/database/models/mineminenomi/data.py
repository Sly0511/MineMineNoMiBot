from datetime import datetime
from typing import Optional
from uuid import UUID

from beanie import Document, Indexed, Link
from pydantic import BaseModel

from data.models import Ability, DevilFruit, Factions, FightingStyles, Races, SubRaces

from ..user import User


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
    abilities: list[Ability]


class Player(Document):
    uuid: Indexed(UUID, unique=True)
    user: Optional[Link[User]] = None
    name: str
    last_update: datetime
    stats: PlayerStats
