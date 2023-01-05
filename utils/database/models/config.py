from pydantic import BaseModel


class BotConfig(BaseModel):
    token: str
    prefix: str
    owners: list[int]
    admins: list[int]
    blacklist: list[int]


class DatabaseConfig(BaseModel):
    name: str


class Config(BaseModel):
    bot: BotConfig
    database: DatabaseConfig
