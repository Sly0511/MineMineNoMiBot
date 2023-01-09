from beanie import Document, Indexed, Link

from .guild import Guild
from .user import User


class Member(Document):
    user_id: Indexed(int)
    guild_id: Indexed(int)
    user: Link[User]
    guild: Link[Guild]
