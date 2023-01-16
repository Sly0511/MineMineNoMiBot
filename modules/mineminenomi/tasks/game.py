from datetime import datetime, timedelta
from json import load
from pathlib import Path

from discord import Embed
from discord.ext import commands, tasks
from pysftp import CnOpts, Connection
from python_nbt.nbt import read_from_nbt_file

from data.models import DevilFruit, DevilFruitRarity, FruitStatus
from utils import chunks
from utils.mineminenomi import NBTParser, run_rcon_command


class FTPHandler:
    def __init__(self, ftp_config):
        cnopts = CnOpts()
        cnopts.hostkeys = None
        self.client = Connection(
            host=ftp_config.host,
            port=ftp_config.port,
            username=ftp_config.user,
            password=ftp_config.password,
            cnopts=cnopts,
        )


class GameTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_folder = Path("cache")
        self.game_cache_folder = self.cache_folder.joinpath("game")
        self.player_cache_folder = self.cache_folder.joinpath("player")
        self.stats_cache_folder = self.cache_folder.joinpath("stats")
        self.logs_cache_folder = self.cache_folder.joinpath("logs")
        self.bot.server_status = None

    async def cog_load(self):
        self.game_cache_folder.mkdir(parents=True, exist_ok=True)
        self.player_cache_folder.mkdir(parents=True, exist_ok=True)
        self.stats_cache_folder.mkdir(parents=True, exist_ok=True)
        self.logs_cache_folder.mkdir(parents=True, exist_ok=True)
        self.retrieve_data.start()
        self.devil_fruit_panel.start()

    async def cog_unload(self):
        self.retrieve_data.cancel()
        self.devil_fruit_panel.cancel()

    def check_server_status(self):
        was_first = self.bot.server_status is None
        status = bool(run_rcon_command(self.bot, "list"))
        if self.bot.server_status == status:
            return
        self.bot.server_status = status
        self.bot.logger.warning("Server is " + ("online" if self.bot.server_status else "offline"))
        if not was_first:
            self.bot.dispatch("server_status", self.bot.server_status)

    async def download_data(self):
        time = datetime.utcnow()
        ftp = FTPHandler(self.bot.config.mineminenomi.ftp)
        with ftp.client as sftp:
            with sftp.cd():
                sftp.get(
                    "usernamecache.json",
                    self.game_cache_folder.joinpath("usernamecache.json"),
                )
                self.bot.logger.debug("Downloaded 'usernamecache.json' from the server.")
            with sftp.cd("World/data/"):
                sftp.get(
                    "mineminenomi.dat",
                    self.game_cache_folder.joinpath("mineminenomi.dat"),
                )
                self.bot.logger.debug("Downloaded 'mineminenomi.dat' from the server.")
            with sftp.cd("World/playerdata/"):
                for file in sftp.listdir_attr():
                    filepath = Path(file.filename)
                    if filepath.suffix != ".dat":
                        continue
                    local_file = self.player_cache_folder.joinpath(filepath.name)
                    if local_file.exists():
                        if (
                            time - timedelta(minutes=5) > datetime.utcfromtimestamp(file.st_mtime)
                            and local_file.stat().st_size == file.st_size
                        ):
                            continue
                    sftp.get(filepath.name, self.player_cache_folder.joinpath(filepath.name))
                    self.bot.logger.debug(f"Downloaded '{filepath.name}' from the server.")
            with sftp.cd("World/stats/"):
                for file in sftp.listdir_attr():
                    filepath = Path(file.filename)
                    if filepath.suffix != ".json":
                        continue
                    local_file = self.stats_cache_folder.joinpath(filepath.name)
                    if local_file.exists():
                        if (
                            time - timedelta(minutes=5) > datetime.utcfromtimestamp(file.st_mtime)
                            and local_file.stat().st_size == file.st_size
                        ):
                            continue
                    sftp.get(filepath.name, self.stats_cache_folder.joinpath(filepath.name))
                    self.bot.logger.debug(f"Downloaded '{filepath.name}' from the server.")
            with sftp.cd("logs/"):
                for file in sftp.listdir_attr():
                    filepath = Path(file.filename)
                    local_file = self.logs_cache_folder.joinpath(filepath.name)
                    local_log_file = self.logs_cache_folder.joinpath(filepath.name).with_suffix("")
                    if local_log_file.exists() or (filepath.suffix == ".gz" and filepath.stem.startswith("debug")):
                        continue
                    if local_file.exists():
                        if (
                            time - timedelta(minutes=5) > datetime.utcfromtimestamp(file.st_mtime)
                            and local_file.stat().st_size == file.st_size
                        ):
                            continue
                    sftp.get(filepath.name, self.logs_cache_folder.joinpath(filepath.name))
                    self.bot.logger.debug(f"Downloaded '{filepath.name}' from the server.")

    @tasks.loop(seconds=60)
    async def retrieve_data(self):
        await self.bot.wait_until_ready()
        self.check_server_status()
        await self.download_data()
        await self.game_data()
        await self.player_data()

    async def game_data(self):
        game = self.game_cache_folder.joinpath("mineminenomi.dat")
        game_data_bytes = game.open("rb")
        game_data_nbt = read_from_nbt_file(game_data_bytes)
        game_data = game_data_nbt.json_obj(full_json=True)
        game_data = NBTParser.parse(game_data)
        self.bot.devil_fruits = []
        devil_fruits_data = load(Path("data/fruits.json").open())
        one_fruits = {oneFruit["fruit"]: oneFruit for oneFruit in game_data["data"]["oneFruitList"]}
        for box_tier, fruits in devil_fruits_data.items():
            for fruit in fruits:
                for qualified_name, fruit_metadata in fruit.items():
                    if qualified_name not in one_fruits.keys():
                        self.bot.devil_fruits.append(
                            DevilFruit(
                                name=fruit_metadata["name"],
                                format_name=fruit_metadata["format_name"],
                                qualified_name=qualified_name,
                                rarity=box_tier,
                                mod_data={
                                    "fruit": qualified_name,
                                    "status": "NEVER_FOUND",
                                    "lastUpdate": datetime.utcnow(),
                                    "history": [],
                                },
                            )
                        )
                        continue
                    for oneFruit in game_data["data"]["oneFruitList"]:
                        if oneFruit["fruit"] == qualified_name:
                            self.bot.devil_fruits.append(
                                DevilFruit(
                                    name=fruit_metadata["name"],
                                    format_name=fruit_metadata["format_name"],
                                    qualified_name=qualified_name,
                                    rarity=box_tier,
                                    mod_data=oneFruit,
                                )
                            )
        self.bot.dispatch("game_data_read", game_data["data"])

    async def player_data(self):
        players = []
        for player in self.player_cache_folder.glob("*.dat"):
            player_data_bytes = player.open("rb")
            player_data_nbt = read_from_nbt_file(player_data_bytes)
            player_data = player_data_nbt.json_obj(full_json=True)
            players.append(NBTParser.parse(player_data))
        self.bot.dispatch("player_data_read", players)

    @tasks.loop(seconds=60)
    async def devil_fruit_panel(self):
        await self.bot.wait_until_ready()
        if not getattr(self.bot, "devil_fruits", []):
            return
        emojis = {
            DevilFruitRarity.GOLDEN: self.bot.get_emoji(1063927592903786636),
            DevilFruitRarity.IRON: self.bot.get_emoji(1063927594816381079),
            DevilFruitRarity.WOODEN: self.bot.get_emoji(1063927590060048405),
        }
        e = Embed(
            title="{g}{i}{w}Available Devil Fruits {w}{i}{g}".format(
                g=str(emojis[DevilFruitRarity.GOLDEN]),
                i=str(emojis[DevilFruitRarity.IRON]),
                w=str(emojis[DevilFruitRarity.WOODEN]),
            ),
            color=0xFFD400,
            timestamp=datetime.utcnow(),
        )
        available_fruits = [
            f"{emojis[fruit.rarity]} {fruit.format_name}"
            for fruit in sorted(
                self.bot.devil_fruits,
                key=lambda x: [
                    (DevilFruitRarity.GOLDEN, DevilFruitRarity.IRON, DevilFruitRarity.WOODEN).index(x.rarity),
                    x.format_name,
                ],
            )
            if fruit.mod_data.status in (FruitStatus.never_found, FruitStatus.lost)
        ]
        available_fruits = chunks(available_fruits, 8)
        for fruits in available_fruits:
            if (len(e.fields) - 2) % 3 in [2, 5, 8, 11, 14]:
                e.add_field(name="\u200b", value="\u200b")
            e.add_field(
                name="\u200b",
                value="\n".join(fruits),
            )
        e.set_footer(text="Updates every 5 minutes | Last updated")
        channel = self.bot.get_channel(self.bot.config.mineminenomi.devil_fruits.panel_channel)
        if not channel:
            return self.bot.logger.warning("The available fruits panel channel ID is invalid.")
        async for message in channel.history(limit=10):
            if message.author.id != self.bot.user.id:
                self.bot.logger.info("1")
                continue
            if not message.embeds or message.embeds[0].title != e.title:
                self.bot.logger.info("2")
                continue
            return await message.edit(embed=e)
        await channel.send(embed=e)


async def setup(bot):
    await bot.add_cog(GameTasks(bot))
