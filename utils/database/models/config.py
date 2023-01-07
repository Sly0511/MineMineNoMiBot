from pydantic import BaseModel


class BotConfig(BaseModel):
    token: str
    prefix: str
    server: int
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


class MineMinenoMiConfig(BaseModel):
    ftp: FTPConfig
    rcon: RconConfig
    races: RacesConfig
    factions: FactionsConfig
    fighting_styles: FightingStylesConfig


class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
    mineminenomi: MineMinenoMiConfig
