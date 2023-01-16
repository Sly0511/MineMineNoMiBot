from discord.ext import commands


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Display the bot's latency to discord")
    async def ping_cmd(self, ctx):
        await ctx.send(f"🏓 Pong! {round(self.bot.latency*1000)}ms")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))
