from discord.ext import commands
from utils.checks import in_bot_admins, in_bot_owners


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="parse", with_app_command=False)
    @commands.guild_only()
    @in_bot_owners()
    async def cmd_parse(self, ctx):
        ...

    @commands.hybrid_command(name="load_cog", with_app_command=False)
    @commands.guild_only()
    @in_bot_admins()
    async def cmd_load_cog(self, ctx):
        ...

    @commands.hybrid_command(name="unload_cog", with_app_command=False)
    @commands.guild_only()
    @in_bot_admins()
    async def cmd_unload_cog(self, ctx):
        ...

    @commands.hybrid_command(name="reload_cog", with_app_command=False)
    @commands.guild_only()
    @in_bot_admins()
    async def cmd_reload_cog(self, ctx):
        ...


async def setup(bot):
    await bot.add_cog(Admin(bot))
