from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from beanie import before_event, Document, Indexed, Insert, Replace, SaveChanges, Update
from pydantic import BaseModel, validator

from utils.mineminenomi import int_array_to_uuid


class CrewChannel(BaseModel):
    role_id: int = None
    text_channel_id: int = None
    voice_channel_id: int = None


class CrewMember(BaseModel):
    id: Optional[Union[UUID, list[int, int, int, int]]]
    username: str
    isCaptain: bool

    @validator("id", always=True)
    def get_uuid(cls, value, values) -> UUID:
        if isinstance(value, list):
            return int_array_to_uuid(value)
        return value


class Crew(Document):
    name: Indexed(str, unique=True)
    jollyRoger: dict
    members: list[CrewMember]
    last_update: datetime = datetime.utcnow()
    created_at: datetime = datetime.utcnow()
    discord_data: CrewChannel = CrewChannel()
    disbanded: bool = False

    @before_event(Insert, Replace, SaveChanges, Update)
    def update_time(self):
        self.last_update = datetime.utcnow()
