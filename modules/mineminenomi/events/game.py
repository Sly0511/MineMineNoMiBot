from datetime import datetime, timedelta

from beanie.operators import Set
from discord.ext import commands

from utils.database.models.mineminenomi import Crew


class GameEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_game_data_read")
    async def on_player_data_read(self, data):
        for crew_data in data["crews"]:
            crew_data["disbanded"] = not bool(len(crew_data['members']))
            await Crew.find_one(Crew.name == crew_data["name"]).upsert(
                Set(crew_data),
                on_insert=Crew(**crew_data)
            )

    @commands.Cog.listener("on_server_status")
    async def server_status_event(self, status):
        if status:
            self.bot.logger.info("Server is now online.")
        else:
            self.bot.logger.info("Server is now offline.")


async def setup(bot):
    await bot.add_cog(GameEvents(bot))
