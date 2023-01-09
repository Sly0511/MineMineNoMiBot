from enum import Enum

from pydantic import BaseModel, validator


class AbilityUnlock(Enum):
    Command = "COMMAND"
    Progression = "PROGRESSION"


class AbilityState(Enum):
    Standby = "STANDBY"


class Ability(BaseModel):
    unlock: AbilityUnlock
    displayName: str
    customTexture: str
    pools: list[int]
    id: str
    state: AbilityState

    @validator("id", always=True)
    def get_uuid(cls, value, values):
        return value.split(":")[-1]
