from discord.ext import commands, tasks
from pathlib import Path
from asyncio import sleep
from python_nbt.nbt import read_from_nbt_file
from utils.mineminenomi import NBTParser
from pysftp import Connection, CnOpts


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
        ftp = FTPHandler(self.bot.config.mineminenomi.ftp)
        with ftp.client as sftp:
            with sftp.cd():
                print(list(sftp.listdir()))

    @tasks.loop(seconds=1)
    async def retrieve_data(self):
        await sleep(300)
        await self.download_data()

    @tasks.loop(minutes=3)
    async def game_data(self):
        game = self.game_cache_folder.joinpath("mineminenomi.dat")
        game_data_bytes = game.open("rb")
        game_data_nbt = read_from_nbt_file(game_data_bytes)
        game_data = game_data_nbt.json_obj(full_json=True)
        game_data = NBTParser.parse(game_data)
        self.bot.dispatch("game_data_read", game_data)

    @tasks.loop(minutes=3)
    async def player_data(self):
        players = []
        for player in self.player_cache_folder.glob("*.dat"):
            player_data_bytes = player.open("rb")
            player_data_nbt = read_from_nbt_file(player_data_bytes)
            player_data = player_data_nbt.json_obj(full_json=True)
            players.append(NBTParser.parse(player_data))
        self.bot.dispatch("player_data_read", players)


async def setup(bot):
    await bot.add_cog(GameTasks(bot))
