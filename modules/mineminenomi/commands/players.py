from discord.ext import commands
from discord import app_commands, File
from data.models import Races, FightingStyles, Factions
import matplotlib.pyplot as plt
from io import BytesIO
from utils.database.models import Player


class PlayerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="factions_population", description="Shows population distribution across factions.")
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
        await interaction.response.send_message(file=File(image, filename="factions.png"))

    @app_commands.command(
        name="fighting_styles_population", description="Shows population distribution across fighting styles."
    )
    async def get_fighting_styles_population(self, interaction):
        players = [player async for player in Player.find_many()]
        swordsman = [p for p in players if p.stats.fighting_style == FightingStyles.Swordsman]
        sniper = [p for p in players if p.stats.fighting_style == FightingStyles.Sniper]
        doctor = [p for p in players if p.stats.fighting_style == FightingStyles.Doctor]
        brawler = [p for p in players if p.stats.fighting_style == FightingStyles.Brawler]
        blackleg = [p for p in players if p.stats.fighting_style == FightingStyles.BlackLeg]
        artofweather = [p for p in players if p.stats.fighting_style == FightingStyles.ArtofWeather]
        populations = [len(swordsman), len(sniper), len(doctor), len(brawler), len(blackleg), len(artofweather)]
        labels = ["Swordsman", "Sniper", "Doctor", "Brawler", "Black Leg", "Art of Weather"]
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
        await interaction.response.send_message(file=File(image, filename="fighting_styles.png"))

    @app_commands.command(name="races_population", description="Shows population distribution across races.")
    async def get_races_population(self, interaction):
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
        await interaction.response.send_message(file=File(image, filename="races.png"))


async def setup(bot):
    await bot.add_cog(PlayerCommands(bot))
