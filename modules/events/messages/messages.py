from discord.ext import commands


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_receive(self, message):
        ctx: commands.Context = await self.bot.get_context(message)
        if await self.can_run(ctx):
            await self.process_command(ctx.message)

    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(self, message):
        ctx: commands.Context = await self.bot.get_context(message)
        if await self.can_run(ctx):
            await self.process_command(ctx.message)

    async def can_run(self, ctx: commands.Context) -> bool:
        if ctx.author.bot:
            return False
        if ctx.author.id in self.bot.config.owners:
            return False
        if ctx.author.id in self.bot.config.blacklist:
            return False
        return True

    async def process_command(self, message):
        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(MessageEvents(bot))
