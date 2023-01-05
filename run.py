from pathlib import Path

from beanie import init_beanie
from discord import Intents
from discord.errors import LoginFailure
from discord.ext.commands import AutoShardedBot
from motor.motor_asyncio import AsyncIOMotorClient
from toml import load

from utils.database.models import Config
from utils.modules import Module


class PyBot(AutoShardedBot):
    def __init__(self):
        self.config = None
        self.modules = []
        self.load_config()
        super(PyBot, self).__init__(
            command_prefix=self.handle_prefix,
            intents=self.get_intents(),
        )

    def load_config(self):
        self.config = Config(**load("config.toml"))

    async def handle_prefix(self):
        return self.config.bot.prefix

    def get_intents(self):
        return Intents.all()

    async def start_database(self):
        client = AsyncIOMotorClient()
        await init_beanie(
            database=getattr(client, self.config.database.name), document_models=[]
        )
        print("Started database")

    async def load_modules(self):
        modules_path = Path("modules")
        for module in modules_path.rglob("*.py"):
            try:
                module = Module.create(module)
            except FileNotFoundError as e:
                print(f"Skipped loading module in \"{module}\": {e}")
                continue
            self.modules.append(module)
        self.modules.sort(key=lambda x: x.info.priority)
        for module in self.modules:
            if module.info.enabled:
                await self.load_extension(module.spec)
                print(f"Loaded {module.info.name}")

    async def setup_hook(self):
        self.load_config()
        await self.start_database()
        await self.load_modules()
        ...


if __name__ == "__main__":
    bot = PyBot()
    try:
        bot.run(bot.config.bot.token, reconnect=True)
    except LoginFailure as e:
        print(
            f"Error: {e}\nCouldn't connect to Discord, are you sure you put a valid token in config.toml?"
        )
