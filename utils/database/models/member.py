from beanie import Document, Link
from .user import User
from .guild import Guild


class Member(Document):
    user: Link[User]
    guild: Link[Guild]
