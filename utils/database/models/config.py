from pydantic import BaseModel


class BotConfig(BaseModel):
    token: str
    prefix: str
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


class MineMinenoMiConfig(BaseModel):
    ftp: FTPConfig
    rcon: RconConfig


class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
    mineminenomi: MineMinenoMiConfig
