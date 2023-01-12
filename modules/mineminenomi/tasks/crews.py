from discord.ext import commands, tasks
from utils.database.models.mineminenomi import Crew, Player
from discord import PermissionOverwrite


class CrewTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manage_discord_crews.start()

    async def cog_unload(self):
        self.manage_discord_crews.cancel()

    @tasks.loop(seconds=60)
    async def manage_discord_crews(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.bot.config.bot.server)
        category = self.bot.get_channel(self.bot.config.mineminenomi.crews.category)
        if not category:
            self.bot.logger.warning("Crew channels task disabled, category ID not valid")
            self.manage_discord_crews.cancel()
            return
        async for crew in Crew.find_many():
            if crew.disbanded:
                if not any(
                    (crew.discord_data.role_id,
                    crew.discord_data.text_channel_id,
                    crew.discord_data.voice_channel_id)
                ):
                    continue
                if role := guild.get_role(crew.discord_data.role_id):
                    await role.delete(reason="Crew disbanded")
                if text_channel := guild.get_channel(crew.discord_data.text_channel_id):
                    await text_channel.delete(reason="Crew disbanded")
                if voice_channel := guild.get_channel(crew.discord_data.voice_channel_id):
                    await voice_channel.delete(reason="Crew disbanded")
                crew.discord_data.role_id = None
                crew.discord_data.text_channel_id = None
                crew.discord_data.voice_channel_id = None
                await crew.save()
                continue
            if not all(
                (crew.discord_data.role_id,
                crew.discord_data.text_channel_id,
                crew.discord_data.voice_channel_id)
            ):
                role = guild.get_role(crew.discord_data.role_id)
                if role:
                    await role.delete()
                text_channel = guild.get_channel(crew.discord_data.text_channel_id)
                if text_channel:
                    await text_channel.delete()
                voice_channel = guild.get_channel(crew.discord_data.voice_channel_id)
                if voice_channel:
                    await voice_channel.delete()
                role = await guild.create_role(name=crew.name)
                text_channel = await category.create_text_channel(
                    name=crew.name,
                    overwrites={
                        guild.default_role: PermissionOverwrite(read_messages=False),
                        role: PermissionOverwrite(read_messages=True)
                    }
                )
                voice_channel = await category.create_voice_channel(
                    name=crew.name,
                    overwrites={
                        guild.default_role: PermissionOverwrite(view_channel=False),
                        role: PermissionOverwrite(view_channel=True)
                    }
                )
                crew.discord_data.role_id = role.id
                crew.discord_data.text_channel_id = text_channel.id
                crew.discord_data.voice_channel_id = voice_channel.id
                await crew.save()
            role = guild.get_role(crew.discord_data.role_id)
            members = [
                crewmate.user.user_id
                for member in crew.members
                if (crewmate := await Player.find_one(Player.uuid == member.id and Player.user != None, fetch_links=True))
            ]
            for member in members:
                user = guild.get_member(member)
                if not user:
                    continue
                if role not in user.roles:
                    await user.add_roles(role)
            for rmember in role.members:
                if rmember.id not in members:
                    await rmember.remove_roles(role)


async def setup(bot):
    await bot.add_cog(CrewTasks(bot))
