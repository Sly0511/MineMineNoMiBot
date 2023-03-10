from pydantic import BaseModel


class BotConfig(BaseModel):
    token: str
    prefix: str
    server: int
    server_name: str
    owners: list[int]
    admins: list[int]
    blacklist: list[int]


class DatabaseConfig(BaseModel):
    name: str


class FTPConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str


class RconConfig(BaseModel):
    host: str
    port: int
    password: str


class DevilFruitsConfig(BaseModel):
    panel_channel: int


class RacesConfig(BaseModel):
    cyborg: int
    fishman: int
    human: int
    mink: int


class FactionsConfig(BaseModel):
    bounty_hunter: int
    marine: int
    pirate: int
    revolutionary: int


class FightingStylesConfig(BaseModel):
    art_of_weather: int
    black_leg: int
    brawler: int
    doctor: int
    sniper: int
    swordsman: int


class CrewsConfig(BaseModel):
    category: int


class MineMinenoMiConfig(BaseModel):
    ftp: FTPConfig
    rcon: RconConfig
    devil_fruits: DevilFruitsConfig
    races: RacesConfig
    factions: FactionsConfig
    fighting_styles: FightingStylesConfig
    crews: CrewsConfig


class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
    mineminenomi: MineMinenoMiConfig
