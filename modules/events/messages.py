from discord.ext import commands

from utils.database.models import Guild, Member, User


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_receive(self, message):
        ctx: commands.Context = await self.bot.get_context(message)
        if await self.can_run(ctx):
            await self.process_command(ctx.message)

    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(self, before, after):
        if before.content == after.content:
            return
        ctx: commands.Context = await self.bot.get_context(after)
        if await self.can_run(ctx):
            await self.process_command(ctx.message)

    async def can_run(self, ctx: commands.Context) -> bool:
        if ctx.author.id in self.bot.config.bot.owners:
            return True
        if ctx.author.bot:
            return False
        if ctx.guild is None:
            return False
        if ctx.author.id in self.bot.config.bot.blacklist:
            return False
        return True

    async def ensure_database(self, ctx: commands.Context):
        if not (guild := await Guild.find_one(Guild.guild_id == ctx.guild.id)):
            guild = await Guild(guild_id=ctx.guild.id).insert()
        if not (user := await User.find_one(User.user_id == ctx.author.id)):
            user = await User(user_id=ctx.author.id).insert()
        if not (member := await Member.find_one(Member.guild_id == ctx.guild.id and Member.user_id == ctx.author.id)):
            member = await Member(guild_id=ctx.guild.id, user_id=ctx.author.id, user=user, guild=guild).insert()
        return guild, user, member

    async def process_command(self, message):
        await self.ensure_database(message)
        await self.bot.process_commands(message)


async def setup(bot):
    await bot.add_cog(MessageEvents(bot))
