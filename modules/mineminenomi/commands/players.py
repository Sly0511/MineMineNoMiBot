from datetime import datetime
from io import BytesIO
from pathlib import Path
from random import randint
from typing import Optional

import matplotlib.pyplot as plt
from discord import Embed, File, Member, app_commands
from discord.ext import commands

from data.models import Factions, FightingStyles, Races
from utils.database.models.mineminenomi import Player
from utils.discord import CodeButton
from utils.mineminenomi import run_rcon_command


class PlayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="player")
    async def player_cmd(self, ctx):
        ...

    @player_cmd.command(name="link", description="Link a player to a discord account.")
    async def player_link_cmd(self, interaction, *, player: str):
        """Links a player to a discord account."""
        await interaction.response.defer()
        code = randint(1000, 9999)
        command = run_rcon_command(self.bot, f"msg {player} Your Discord link code: {code}")
        if not command:
            return await interaction.followup.send(f"Couldn't connect to the server, it may be offline.")
        if "No player was found" in command:
            return await interaction.followup.send(f"You must be online, check also for typos.")
        embed = Embed(title="Discord Account Link")
        embed.description = (
            'A code was sent to you via private message in minecraft. Click "Input code" and put the code in the box.'
        )
        await interaction.followup.send(
            view=CodeButton(self.bot, interaction.user, player, code),
            embed=embed,
            ephemeral=True,
        )

    @player_cmd.command(name="check", description="Check a player's data")
    async def check_player_cmd(self, ctx, user: Optional[Member], name: Optional[str]):
        if user:
            player = await Player.find_one(Player.user.user_id == user.id, fetch_links=True)
        elif name:
            player = await Player.find_one(Player.name == name)
        else:
            return await ctx.send("Please give a valid username or discord user.")
        if not player:
            return await ctx.send("That user doesn't have a linked account.")
        last_login = Path("cache/player").joinpath(str(player.uuid) + ".dat").stat().st_mtime
        e = Embed(title=f"Player information for {player.name}", timestamp=datetime.utcfromtimestamp(last_login))
        e.add_field(name="Race", value=player.stats.race.value.replace("_", " ").title())
        e.add_field(name="Sub Race", value=player.stats.sub_race.value.replace("_", " ").title() or "N/A")
        e.add_field(name="\u200b", value="\u200b")
        e.add_field(name="Faction", value=player.stats.faction.value.replace("_", " ").title())
        e.add_field(name="Fighting Style", value=player.stats.fighting_style.value.replace("_", " ").title())
        e.add_field(name="\u200b", value="\u200b")
        e.add_field(name="Belly", value=player.stats.belly)
        e.add_field(name="Doriki", value=player.stats.doriki)
        e.add_field(name="\u200b", value="\u200b")
        e.add_field(name="Bounty", value=player.stats.bounty)
        e.add_field(name="Loyalty", value=player.stats.loyalty)
        e.add_field(name="\u200b", value="\u200b")
        haki = f"Busoshoku Haki (Hardening): **{round(player.stats.busoshoku_haki, 2)}**\n"
        haki += f"Kenboshoku Haki (Observation): **{round(player.stats.kenboshoku_haki, 2)}**\n"
        haki += f"Haoshoku Haki (Conqueror): **{round(player.stats.haoshoku_haki, 2)}**\n"
        e.add_field(name="Haki", value=haki)
        e.add_field(name="Haki Limit", value=player.stats.haki_limit)
        e.set_footer(text="Last login")
        await ctx.send(embed=e)

    @commands.hybrid_group(name="population")
    async def population_cmd(self, ctx):
        ...

    @population_cmd.command(
        name="factions",
        description="Shows population distribution across factions.",
    )
    async def get_factions_population(self, ctx):
        players = [player async for player in Player.find_many()]
        pirates = [p for p in players if p.stats.faction == Factions.Pirate]
        marines = [p for p in players if p.stats.faction == Factions.Marine]
        revolut = [p for p in players if p.stats.faction == Factions.Revolutionary]
        bounthr = [p for p in players if p.stats.faction == Factions.BountyHunter]
        populations = [len(pirates), len(marines), len(revolut), len(bounthr)]
        labels = ["Pirates", "Marines", "Revolutionaries", "Bounty hunters"]
        colors = ["#6b0700", "#00276b", "#8a2801", "#256b00"]
        _, ax1 = plt.subplots()
        _, texts, autotexts = ax1.pie(populations, colors=colors, labels=labels, autopct="%1.1f%%", startangle=90)
        for text in texts:
            text.set_color("#ccc")
        for autotext in autotexts:
            autotext.set_color("#ccc")
        centre_circle = plt.Circle((0, 0), 0.70, fc="#0000")
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.axis("equal")
        image = BytesIO()
        plt.savefig(image, facecolor="#0000", format="PNG")
        image.seek(0)
        await ctx.send(file=File(image, filename="factions.png"))

    @population_cmd.command(
        name="fighting_styles",
        description="Shows population distribution across fighting styles.",
    )
    async def get_fighting_styles_population(self, ctx):
        players = [player async for player in Player.find_many()]
        swordsman = [p for p in players if p.stats.fighting_style == FightingStyles.Swordsman]
        sniper = [p for p in players if p.stats.fighting_style == FightingStyles.Sniper]
        doctor = [p for p in players if p.stats.fighting_style == FightingStyles.Doctor]
        brawler = [p for p in players if p.stats.fighting_style == FightingStyles.Brawler]
        blackleg = [p for p in players if p.stats.fighting_style == FightingStyles.BlackLeg]
        artofweather = [p for p in players if p.stats.fighting_style == FightingStyles.ArtofWeather]
        populations = [
            len(swordsman),
            len(sniper),
            len(doctor),
            len(brawler),
            len(blackleg),
            len(artofweather),
        ]
        labels = [
            "Swordsman",
            "Sniper",
            "Doctor",
            "Brawler",
            "Black Leg",
            "Art of Weather",
        ]
        _, ax1 = plt.subplots()
        _, texts, autotexts = ax1.pie(populations, labels=labels, autopct="%1.1f%%", startangle=90)
        for text in texts:
            text.set_color("#ccc")
        for autotext in autotexts:
            autotext.set_color("#ccc")
        centre_circle = plt.Circle((0, 0), 0.70, fc="#0000")
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.axis("equal")
        image = BytesIO()
        plt.savefig(image, facecolor="#0000", format="PNG")
        image.seek(0)
        await ctx.send(file=File(image, filename="fighting_styles.png"))

    @population_cmd.command(
        name="races",
        description="Shows population distribution across races.",
    )
    async def get_races_population(self, ctx):
        players = [player async for player in Player.find_many()]
        human = [p for p in players if p.stats.race == Races.Human]
        cyborg = [p for p in players if p.stats.race == Races.Cyborg]
        mink = [p for p in players if p.stats.race == Races.Mink]
        fishman = [p for p in players if p.stats.race == Races.Fishman]
        populations = [len(human), len(cyborg), len(mink), len(fishman)]
        labels = ["Human", "Cyborg", "Mink", "Fishman"]
        _, ax1 = plt.subplots()
        _, texts, autotexts = ax1.pie(populations, labels=labels, autopct="%1.1f%%", startangle=90)
        for text in texts:
            text.set_color("#ccc")
        for autotext in autotexts:
            autotext.set_color("#ccc")
        centre_circle = plt.Circle((0, 0), 0.70, fc="#0000")
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax1.axis("equal")
        image = BytesIO()
        plt.savefig(image, facecolor="#0000", format="PNG")
        image.seek(0)
        await ctx.send(file=File(image, filename="races.png"))


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
