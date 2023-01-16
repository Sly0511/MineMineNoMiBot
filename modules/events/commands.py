from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound


class CommandsEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_command")
    async def on_command_event(self, ctx):
        self.bot.logger.info(f'{ctx.author} used command "{ctx.command}"')

    @commands.Cog.listener("on_command_error")
    async def on_command_error_event(self, ctx, error: commands.errors.CommandInvokeError):
        if isinstance(error, CommandNotFound):
            return
        else:
            await ctx.send("This command has errored.")
            raise error.original


async def setup(bot):
    await bot.add_cog(CommandsEvents(bot))
