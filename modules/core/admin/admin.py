from discord.ext import commands
from utils.checks import in_bot_admins, in_bot_owners, is_bot_owners_interaction
import traceback
from datetime import datetime
import re
from discord import app_commands, File, Object
import os
from utils.discord import Traceback
from mcrcon import MCRcon


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="parse", with_app_command=False)
    @commands.guild_only()
    @in_bot_owners()
    async def cmd_parse(self, ctx):
        """Parse a bit of code as a command."""
        code = re.findall(r"(?i)(?s)```py\n(.*?)```", ctx.message.content)
        if not code:
            return await ctx.send("No code detected.", ephemeral=True)
        code = "    " + code[0].replace("\n", "\n    ")
        code = "async def __eval_function__():\n" + code
        # Base Variables
        async def to_file(text, format="json"):
            _f = f"file.{format}"
            with open(_f, "w+") as f:
                f.write(text)
            await ctx.send(file=File(_f))
            os.remove(_f)

        additional = {}
        additional["self"] = self
        additional["feu"] = self.bot.fetch_user
        additional["fem"] = ctx.channel.fetch_message
        additional["dlt"] = ctx.message.delete
        additional["now"] = datetime.utcnow()
        additional["nowts"] = int(datetime.utcnow().timestamp())
        additional["ctx"] = ctx
        additional["sd"] = ctx.send
        additional["channel"] = ctx.channel
        additional["author"] = ctx.author
        additional["guild"] = ctx.guild
        additional["to_file"] = to_file
        try:
            exec(code, {**globals(), **additional}, locals())

            await locals()["__eval_function__"]()
        except Exception as error:
            built_error = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            view = Traceback(ctx, built_error)
            await ctx.send(content="An error occured.", view=view)

    @app_commands.command(name="rcon", description="Run a console command.")
    @commands.guild_only()
    @is_bot_owners_interaction()
    async def rcon(self, interaction, command: str):
        rcon_config = self.bot.config.mineminenomi.rcon
        with MCRcon(host=rcon_config.host, password=rcon_config.password, port=rcon_config.port) as rcon:
            response = rcon.command(f"/{command}")
            await interaction.response.send_message(response or "Command ran successfully")

    @commands.hybrid_command(name="update", with_app_command=True)
    @commands.guild_only()
    @in_bot_owners()
    async def cmd_update(self, ctx):
        guild = Object(id=self.bot.config.bot.server)
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)
        await ctx.send("Slash commands were synced!")

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
