import os
import re
import traceback
from datetime import datetime

from discord import Embed, File, Object
from discord.ext import commands

from utils.checks import in_bot_admins, in_bot_owners
from utils.discord import Traceback


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="parse", with_app_command=False)
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

        additional = {
            "self": self,
            "feu": self.bot.fetch_user,
            "fem": ctx.channel.fetch_message,
            "dlt": ctx.message.delete,
            "now": datetime.utcnow(),
            "nowts": int(datetime.utcnow().timestamp()),
            "ctx": ctx,
            "sd": ctx.send,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "to_file": to_file,
        }
        try:
            exec(code, {**globals(), **additional}, locals())

            await locals()["__eval_function__"]()
        except Exception as error:
            built_error = "".join(traceback.format_exception(type(error), error, error.__traceback__))
            view = Traceback(ctx, built_error)
            await ctx.send(content="An error occured.", view=view)

    @commands.hybrid_command(name="update", with_app_command=False)
    @in_bot_owners()
    async def cmd_update(self, ctx):
        guild = Object(id=self.bot.config.bot.server)
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)
        await ctx.send("Slash commands were synced!")

    @commands.hybrid_command(name="modules", with_app_command=False)
    @in_bot_admins()
    async def cmd_list_cog(self, ctx):
        modules, loaded, unloaded = list(self.bot.get_modules())
        e = Embed(title="Modules", color=0x000000)
        em_enabled = "✅"
        em_disabled = "❌"
        em_loaded = "📥"
        em_unloaded = "📤"
        modules.sort(key=lambda x: x.info.name)
        e.description = "\n".join(
            [
                f"{em_enabled if m.info.enabled else em_disabled} {em_loaded if m in loaded else em_unloaded} \
                `{'.'.join(m.spec.split('.')[-2:]):^24s}` {m.info.name}"
                for m in modules
            ]
        )
        await ctx.send(embed=e)

    @commands.hybrid_command(name="reload", with_app_command=False)
    @in_bot_admins()
    async def cmd_load_cog(self, ctx, name: str):
        modules, loaded, unloaded = list(self.bot.get_modules())
        for module in modules:
            if module.spec.endswith(name.lower()):
                if module in unloaded:
                    try:
                        await self.bot.load_extension(module.spec)
                        await ctx.send(f"Loaded `{module.spec}`")
                    except Exception as err:
                        await ctx.send(f"Couldn't load `{module.spec}`: ```{err}```")
                else:
                    try:
                        await self.bot.reload_extension(module.spec)
                        await ctx.send(f"Reloaded `{module.spec}`")
                    except Exception as err:
                        await ctx.send(f"Couldn't reload `{module.spec}`: ```{err}```")

    @commands.hybrid_command(name="unload", with_app_command=False)
    @in_bot_admins()
    async def cmd_unload_cog(self, ctx, name: str):
        modules, loaded, unloaded = list(self.bot.get_modules())
        for module in modules:
            if module.spec.endswith(name.lower()):
                if module in loaded:
                    try:
                        await self.bot.unload_extension(module.spec)
                        await ctx.send(f"Unloaded `{module.spec}`")
                    except Exception as err:
                        await ctx.send(f"Couldn't unload `{module.spec}`: ```{err}```")
                else:
                    await ctx.send(f"`{module.spec} not loaded")


async def setup(bot):
    await bot.add_cog(Admin(bot))
