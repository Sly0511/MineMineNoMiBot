from discord import Embed
from discord.ext import commands
from discord.utils import get
from utils.database.models.mineminenomi import Crew


class CrewCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="crews")
    async def crews_cmd(self, ctx):
        ...

    @crews_cmd.command(name="list")
    async def crews_list(self, ctx):
        e = Embed(title="List of crews", description="")
        crews = Crew.find_many(Crew.disbanded == False)
        e.description += "\n".join(
            [
                f"`{c.name}` Crewmate count: {len(c.members)} "
                async for c in crews
            ]
        )
        await ctx.send(embed=e)

    @crews_cmd.command(name="check")
    async def crews_check(self, ctx, crew_name):
        crew = await Crew.find_one(Crew.name == crew_name and Crew.disbanded == False)
        captain = get(crew.members, isCaptain=True)
        if not crew or not captain:
            return await ctx.send("Crew was not found, make sure to type the name correctly.")
        e = Embed(title=crew.name, timestamp=crew.created_at)
        e.add_field(name="Captain", value=captain.username)
        crewmates = [m.username for m in crew.members if m != captain]
        if crewmates:
            e.add_field(name=f"Crewmates ({len(crewmates)})",
                        value="\n".join([c.username for c in crewmates]), inline=False)
        e.set_footer(text="Crew formed")
        await ctx.send(embed=e)


async def setup(bot):
    await bot.add_cog(CrewCommands(bot))
