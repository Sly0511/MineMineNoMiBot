from json import dumps
from pathlib import Path

from beanie import init_beanie
from discord import Intents
from discord.errors import LoginFailure
from discord.ext.commands import AutoShardedBot
from motor.motor_asyncio import AsyncIOMotorClient
from toml import load

from utils import Logger, Tree
from utils.database.models import Config, Guild, Member, User
from utils.database.models.mineminenomi import Crew, Player
from utils.modules import Module


class PyBot(AutoShardedBot):
    def __init__(self):
        self.logger = Logger()
        self.config = None
        self.load_config()
        super(PyBot, self).__init__(
            command_prefix=self.handle_prefix,
            intents=self.get_intents(),
            tree_cls=Tree,
        )

    def load_config(self):
        config_file = Path("config.toml")
        if not config_file.exists():
            dist_config_file = Path("config_dist.toml")
            if not dist_config_file.exists():
                self.logger.error('Could not find "config_dist.toml". Was it deleted?')
            else:
                with config_file.open("w+") as f:
                    f.write(dist_config_file.read_text())
                    self.logger.warning(
                        'Config file was generated from "config_dist.toml"'
                    )
                    self.logger.warning("Please set the required variables.")
            quit()
        self.config = Config(**load("config.toml"))
        self.logger.debug(
            "Successfully loaded configuration: " + dumps(self.config.json())
        )

    async def handle_prefix(self, bot, message):
        return self.config.bot.prefix

    def get_intents(self):
        return Intents.all()

    async def start_database(self):
        client = AsyncIOMotorClient()
        await init_beanie(
            database=getattr(client, self.config.database.name),
            document_models=[Crew, Guild, User, Member, Player],
        )
        self.logger.info("Database initialized")

    def get_modules(self):
        modules_path = Path("modules")
        modules = []
        for module in modules_path.rglob("*.py"):
            try:
                modules.append(Module.create(module))
            except FileNotFoundError as err:
                self.logger.warning(f'Skipped loading module in "{module}": {err}')
                continue
        modules.sort(key=lambda x: x.info.priority)
        loaded_modules_specs = [v.__module__ for c, v in self.cogs.items()]
        loaded_modules = [m for m in modules if m.spec in loaded_modules_specs]
        unloaded_modules = [m for m in modules if m not in loaded_modules]
        return modules, loaded_modules, unloaded_modules

    async def load_modules(self):
        _, _, modules = self.get_modules()
        self.logger.info(
            f"Found {len(modules)} modules. {', '.join([m.info.name for m in modules])}"
        )
        for module in modules:
            if module.info.enabled:
                await self.load_extension(module.spec)
                self.logger.info(f"Loaded {module.info.name}")
            else:
                self.logger.debug(
                    f"Skipping '{module.info.name}' because it's disabled"
                )
        self.logger.info("Finished loading modules")

    async def setup_hook(self):
        self.load_config()
        await self.start_database()
        await self.load_modules()

    async def on_message(self, message):
        ...


if __name__ == "__main__":
    bot = PyBot()
    try:
        bot.run(bot.config.bot.token, reconnect=True)
    except LoginFailure as e:
        bot.logger.error(
            f"{e}\nCouldn't connect to Discord, are you sure you put a valid token in config.toml?"
        )
