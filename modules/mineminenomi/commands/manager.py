from discord.ext import commands

from utils.checks import is_bot_owners_interaction
from utils.mineminenomi import run_rcon_command


class ManagerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rcon", description="Run a console command.")
    @commands.guild_only()
    @is_bot_owners_interaction()
    async def rcon(self, interaction, command: str):
        await interaction.response.send_message(run_rcon_command(self.bot, command))


async def setup(bot):
    await bot.add_cog(ManagerCommands(bot))