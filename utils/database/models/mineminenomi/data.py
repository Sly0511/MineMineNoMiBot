from pydantic import BaseModel
from beanie import Document, Link, Indexed
from ..user import User
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum


class DevilFruit(BaseModel):
    name: str
    format_name: str
    qualified_name: str
    rarity: str


class Races(Enum):
    Human = "human"
    Cyborg = "cyborg"
    Mink = "mink"
    Fishman = "fishman"


class subRaces(Enum):
    Bunny = "mink_bunny"
    Dog = "mink_dog"
    Lion = "mink_lion"


class Factions(Enum):
    Pirate = "pirate"
    Marine = "marine"
    Revolutionary = "revolutionary"
    BountyHunter = "bounty_hunter"


class FightingStyles(Enum):
    Brawler = "brawler"
    Swordsman = "swordsman"
    BlackLeg = "black_leg"
    Sniper = "sniper"
    Doctor = "doctor"
    ArtofWeather = "art_of_weather"


class PlayerStats(BaseModel):
    race: Optional[Races]
    sub_race: Optional[subRaces]
    faction: Optional[Factions]
    fighting_style: Optional[FightingStyles]
    inventory: list[dict]
    belly: int
    bounty: int
    loyalty: int
    doriki: int
    harderning_haki: float
    imbuing_haki: float
    observation_haki: float
    haoshoku_haki: bool
    haki_limit: float
    last_seen: datetime
    inactive: bool
    devil_fruits: list[DevilFruit]
    eaten_devil_fruits: list[DevilFruit]
    inventory_devil_fruits: list[DevilFruit]


class Player(Document):
    uuid: Indexed(UUID)
    user: Link[User]
    name: str
    last_update: datetime
    stats: PlayerStats
