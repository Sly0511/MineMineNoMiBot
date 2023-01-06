from discord.ext import commands


class PlayerEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_player_data_read")
    async def on_player_data_read(self, data):
        ...


async def setup(bot):
    await bot.add_cog(PlayerEvents(bot))
