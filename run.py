from pathlib import Path

from beanie import init_beanie
from discord import Intents
from discord.errors import LoginFailure
from discord.ext.commands import AutoShardedBot
from motor.motor_asyncio import AsyncIOMotorClient
from toml import load

from utils.database.models import Config, Guild, User, Member
from utils.database.models.mineminenomi import Player
from utils.modules import Module
from utils import Logger, Tree
from json import dumps
from asyncio import Event


class PyBot(AutoShardedBot):
    def __init__(self):
        self.modules_ready = Event()
        self.logger = Logger()
        self.config = None
        self.modules = []
        self.load_config()
        super(PyBot, self).__init__(
            command_prefix=self.handle_prefix,
            intents=self.get_intents(),
            tree_cls=Tree
        )

    def load_config(self):
        self.config = Config(**load("config.toml"))
        self.logger.debug("Successfully loaded configuration: " + dumps(self.config.json()))

    async def handle_prefix(self, bot, message):
        return self.config.bot.prefix

    def get_intents(self):
        return Intents.all()

    async def start_database(self):
        client = AsyncIOMotorClient()
        await init_beanie(
            database=getattr(client, self.config.database.name),
            document_models=[
                Guild,
                User,
                Member,
                Player
            ]
        )
        self.logger.info("Database initialized")

    async def load_modules(self):
        modules_path = Path("modules")
        for module in modules_path.rglob("*.py"):
            try:
                module = Module.create(module)
            except FileNotFoundError as err:
                self.logger.warning(f"Skipped loading module in \"{module}\": {err}")
                continue
            self.modules.append(module)
        self.modules.sort(key=lambda x: x.info.priority)
        self.logger.info(f"Found {len(self.modules)} modules. {', '.join([m.info.name for m in self.modules])}")
        for module in self.modules:
            if module.info.enabled:
                await self.load_extension(module.spec)
                self.logger.info(f"Loaded {module.info.name}")
            else:
                self.logger.debug(f"Skipping '{module.info.name}' because it's disabled")
        self.modules_ready.set()
        self.logger.info("Finished loading modules")

    async def setup_hook(self):
        self.load_config()
        await self.start_database()
        await self.load_modules()


if __name__ == "__main__":
    bot = PyBot()
    try:
        bot.run(bot.config.bot.token, reconnect=True)
    except LoginFailure as e:
        bot.logger.error(
            f"{e}\nCouldn't connect to Discord, are you sure you put a valid token in config.toml?"
        )
