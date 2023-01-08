from discord.ext import commands, tasks
from pathlib import Path
from asyncio import sleep
from python_nbt.nbt import read_from_nbt_file
from utils.mineminenomi import NBTParser
from pysftp import Connection, CnOpts
from datetime import datetime, timedelta
from json import load
from data.models import DevilFruit


class FTPHandler:
    def __init__(self, ftp_config):
        cnopts = CnOpts()
        cnopts.hostkeys = None
        self.client = Connection(
            host=ftp_config.host,
            port=ftp_config.port,
            username=ftp_config.user,
            password=ftp_config.password,
            cnopts=cnopts
        )


class GameTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_folder = Path("cache")
        self.player_cache_folder = self.cache_folder.joinpath("player")
        self.game_cache_folder = self.cache_folder.joinpath("game")
        self.game_data_ready = False

    async def cog_load(self):
        self.cache_folder.mkdir(parents=True, exist_ok=True)
        self.player_cache_folder.mkdir(parents=True, exist_ok=True)
        self.game_cache_folder.mkdir(parents=True, exist_ok=True)
        await self.download_data()
        self.start_tasks()

    async def cog_unload(self):
        self.player_data.cancel()
        self.game_data.cancel()

    def start_tasks(self):
        self.retrieve_data.start()
        self.game_data.start()
        self.player_data.start()

    async def download_data(self):
        time = datetime.utcnow()
        ftp = FTPHandler(self.bot.config.mineminenomi.ftp)
        with ftp.client as sftp:
            with sftp.cd():
                sftp.get('usernamecache.json', self.game_cache_folder.joinpath('usernamecache.json'))
                self.bot.logger.debug("Downloaded 'usernamecache.json' from the server.")
            with sftp.cd("World/data/"):
                sftp.get('mineminenomi.dat', self.game_cache_folder.joinpath('mineminenomi.dat'))
                self.bot.logger.debug("Downloaded 'mineminenomi.dat' from the server.")
            with sftp.cd('World/playerdata/'):
                for file in sftp.listdir_attr():
                    filepath = Path(file.filename)
                    if filepath.suffix == ".dat":
                        continue
                    local_file = self.player_cache_folder.joinpath(filepath.name)
                    if local_file.exists():
                        if time - timedelta(minutes=5) > datetime.utcfromtimestamp(file.st_mtime) \
                                and local_file.stat().st_size == file.st_size:
                            continue
                    sftp.get(filepath.name, self.player_cache_folder.joinpath(filepath.name))
                    self.bot.logger.debug(f"Downloaded '{filepath.name}' from the server.")

    @tasks.loop(seconds=1)
    async def retrieve_data(self):
        await self.bot.modules_ready.wait()
        await sleep(60)
        await self.download_data()

    @tasks.loop(minutes=1)
    async def game_data(self):
        await self.bot.modules_ready.wait()
        game = self.game_cache_folder.joinpath("mineminenomi.dat")
        game_data_bytes = game.open("rb")
        game_data_nbt = read_from_nbt_file(game_data_bytes)
        game_data = game_data_nbt.json_obj(full_json=True)
        game_data = NBTParser.parse(game_data)
        self.bot.devil_fruits = []
        devil_fruits_data = load(Path('data/fruits.json').open())
        one_fruits = {
            oneFruit['fruit']: oneFruit
            for oneFruit in game_data['data']['oneFruitList']
        }
        for box_tier, fruits in devil_fruits_data.items():
            for fruit in fruits:
                for qualified_name, fruit_metadata in fruit.items():
                    if qualified_name not in one_fruits.keys():
                        self.bot.devil_fruits.append(
                            DevilFruit(
                                name=fruit_metadata['name'],
                                format_name=fruit_metadata['format_name'],
                                qualified_name=qualified_name,
                                rarity=box_tier,
                                mod_data={
                                    "fruit": qualified_name,
                                    "status": "LOST",
                                    "lastUpdate": datetime.utcnow(),
                                    "history": []
                                }
                            )
                        )
                        continue
                    for oneFruit in game_data['data']['oneFruitList']:
                        if oneFruit['fruit'] == qualified_name:
                            self.bot.devil_fruits.append(
                                DevilFruit(
                                    name=fruit_metadata['name'],
                                    format_name=fruit_metadata['format_name'],
                                    qualified_name=qualified_name,
                                    rarity=box_tier,
                                    mod_data=oneFruit
                                )
                            )
        self.bot.dispatch("game_data_read", game_data)
        self.game_data_ready = True

    @tasks.loop(minutes=3)
    async def player_data(self):
        await self.bot.modules_ready.wait()
        while not self.game_data_ready:
            await sleep(3)
        players = []
        for player in self.player_cache_folder.glob("*.dat"):
            player_data_bytes = player.open("rb")
            player_data_nbt = read_from_nbt_file(player_data_bytes)
            player_data = player_data_nbt.json_obj(full_json=True)
            players.append(NBTParser.parse(player_data))
        self.bot.dispatch("player_data_read", players)


async def setup(bot):
    await bot.add_cog(GameTasks(bot))
