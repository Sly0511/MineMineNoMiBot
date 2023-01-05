from discord.ext import commands, tasks
from pathlib import Path
from asyncio import sleep
from python_nbt.nbt import read_from_nbt_file
from utils.mineminenomi import NBTParser


class GameTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_folder = Path("cache")
        self.player_cache_folder = self.cache_folder.joinpath("player")
        self.game_cache_folder = self.cache_folder.joinpath("game")
        self.setup()

    async def cog_unload(self):
        self.player_data.cancel()
        self.game_data.cancel()

    def setup(self):
        self.cache_folder.mkdir(parents=True, exist_ok=True)
        self.player_cache_folder.mkdir(parents=True, exist_ok=True)
        self.game_cache_folder.mkdir(parents=True, exist_ok=True)
        self.download_data()
        self.start_tasks()

    def start_tasks(self):
        self.retrieve_data.start()
        self.game_data.start()
        self.player_data.start()

    def download_data(self):
        ...

    @tasks.loop(seconds=1)
    async def retrieve_data(self):
        await sleep(300)
        self.download_data()

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
