from beanie import Document, Indexed


class Guild(Document):
    guild_id: Indexed(int)
    prefixes: list[str] = []
