from beanie import Document, Link, Indexed
from ..user import User
from uuid import UUID


class Player(Document):
    uuid: Indexed(UUID)
    user: Link[User]
