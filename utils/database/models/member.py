from beanie import Document, Link, Indexed
from .user import User
from .guild import Guild


class Member(Document):
    user_id: Indexed(int)
    guild_id: Indexed(int)
    user: Link[User]
    guild: Link[Guild]
