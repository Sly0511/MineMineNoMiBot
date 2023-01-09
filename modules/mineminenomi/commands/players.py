from discord.ext import commands
from discord import app_commands, File, Embed
from data.models import Races, FightingStyles, Factions
import matplotlib.pyplot as plt
from io import BytesIO
from utils.database.models import Player
from random import randint
from mcrcon import MCRcon, MCRconException
from utils.discord import CodeButton


class PlayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="link", description="Link a player to a discord account."
    )
    async def link_player(self, interaction, *, player: str):
        """Links a player to a discord account."""
        await interaction.response.defer()
        code = randint(1000, 9999)
        rcon_config = self.bot.config.mineminenomi.rcon
        with MCRcon(
            host=rcon_config.host, password=rcon_config.password, port=rcon_config.port
        ) as rcon:
            try:
                result = rcon.command(f"/msg {player} Your Discord link code: {code}")
                if "No player was found" in result:
                    return await interaction.followup.send(
                        f"You must be online, check also for typos."
                    )
            except MCRconException:
                return await interaction.followup.send(
                    f"The {self.bot.config.bot.server_name} server isn't responding."
                )
        embed = Embed(title="Discord Account Link")
        embed.description = 'A code was sent to you via private message in minecraft. Click "Input code" and put the code in the box.'
        await interaction.followup.send(
            view=CodeButton(self.bot, interaction.user, player, code),
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(
        name="factions_population",
        description="Shows population distribution across factions.",
    )
    async def get_factions_population(self, interaction):
        players = [player async for player in Player.find_many()]
        pirates = [p for p in players if p.stats.faction == Factions.Pirate]
        marines = [p for p in players if p.stats.faction == Factions.Marine]
        revolut = [p for p in players if p.stats.faction == Factions.Revolutionary]
        bounthr = [p for p in players if p.stats.faction == Factions.BountyHunter]
        populations = [len(pirates), len(marines), len(revolut), len(bounthr)]
        labels = ["Pirates", "Marines", "Revolutionaries", "Bounty hunters"]
        colors = ["#6b0700", "#00276b", "#8a2801", "#256b00"]
        _, ax1 = plt.subplots()
        _, texts, autotexts = ax1.pie(
            populations, colors=colors, labels=labels, autopct="%1.1f%%", startangle=90
        )
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
        await interaction.response.send_message(
            file=File(image, filename="factions.png")
        )

    @app_commands.command(
        name="fighting_styles_population",
        description="Shows population distribution across fighting styles.",
    )
    async def get_fighting_styles_population(self, interaction):
        players = [player async for player in Player.find_many()]
        swordsman = [
            p for p in players if p.stats.fighting_style == FightingStyles.Swordsman
        ]
        sniper = [p for p in players if p.stats.fighting_style == FightingStyles.Sniper]
        doctor = [p for p in players if p.stats.fighting_style == FightingStyles.Doctor]
        brawler = [
            p for p in players if p.stats.fighting_style == FightingStyles.Brawler
        ]
        blackleg = [
            p for p in players if p.stats.fighting_style == FightingStyles.BlackLeg
        ]
        artofweather = [
            p for p in players if p.stats.fighting_style == FightingStyles.ArtofWeather
        ]
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
        _, texts, autotexts = ax1.pie(
            populations, labels=labels, autopct="%1.1f%%", startangle=90
        )
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
        await interaction.response.send_message(
            file=File(image, filename="fighting_styles.png")
        )

    @app_commands.command(
        name="races_population",
        description="Shows population distribution across races.",
    )
    async def get_races_population(self, interaction):
        players = [player async for player in Player.find_many()]
        human = [p for p in players if p.stats.race == Races.Human]
        cyborg = [p for p in players if p.stats.race == Races.Cyborg]
        mink = [p for p in players if p.stats.race == Races.Mink]
        fishman = [p for p in players if p.stats.race == Races.Fishman]
        populations = [len(human), len(cyborg), len(mink), len(fishman)]
        labels = ["Human", "Cyborg", "Mink", "Fishman"]
        _, ax1 = plt.subplots()
        _, texts, autotexts = ax1.pie(
            populations, labels=labels, autopct="%1.1f%%", startangle=90
        )
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
        await interaction.response.send_message(file=File(image, filename="races.png"))


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
