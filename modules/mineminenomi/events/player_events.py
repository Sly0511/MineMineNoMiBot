import re
from datetime import datetime, timedelta
from json import load
from pathlib import Path

from discord.ext import commands, tasks

from utils.database.models.mineminenomi import Player
from utils.mineminenomi import int_array_to_uuid, run_rcon_command


class PlayerEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.online_players = {
            "last_update": datetime.utcfromtimestamp(0),
            "players": [],
        }

    async def cog_load(self):
        self.manage_roles.start()

    def get_online_players(self):
        if self.online_players["last_update"] < datetime.utcnow() - timedelta(seconds=30):
            result = run_rcon_command(self.bot, "list")
            if not result:
                return
            self.online_players["last_update"] = datetime.utcnow()
            self.online_players["players"] = re.findall("(\w{2,16})(?:,|$)", result)
        return self.online_players["players"]

    @commands.Cog.listener("on_player_data_read")
    async def on_player_data_read(self, data):
        username_cache = load(Path("cache/game/usernamecache.json").open())
        for player in data:
            uuid = int_array_to_uuid(player["UUID"])
            haki_data = player["ForgeCaps"]["mineminenomi:haki_data"]
            devil_fruit = player["ForgeCaps"]["mineminenomi:devil_fruit"]
            entity_stats = player["ForgeCaps"]["mineminenomi:entity_stats"]
            ability_data = player["ForgeCaps"]["mineminenomi:ability_data"]
            total_haki = haki_data["busoHakiExp"] + haki_data["kenHakiExp"]
            eaten_devil_fruits = [
                df
                for df in self.bot.devil_fruits
                if df.qualified_name == devil_fruit["devilFruit"] or devil_fruit["hasYamiPower"]
            ]
            inventory_devil_fruits = [
                df
                for item in player["Inventory"]
                for df in self.bot.devil_fruits
                if df.name == item["id"].split(":")[1]
            ]
            devil_fruits = eaten_devil_fruits + inventory_devil_fruits
            haoshoku = False
            for ability in ability_data["unlocked_abilities"]:
                if ability["id"] == "mineminenomi:haoshoku_haki":
                    haoshoku = True
            player_entry = Player(
                uuid=uuid,
                name=username_cache.get(str(uuid), "Unknown"),
                stats={
                    "race": entity_stats["race"],
                    "sub_race": entity_stats["subRace"],
                    "faction": entity_stats["faction"],
                    "fighting_style": entity_stats["fightingStyle"],
                    "inventory": player["Inventory"],
                    "belly": entity_stats["belly"],
                    "bounty": entity_stats["bounty"],
                    "loyalty": entity_stats["loyalty"],
                    "doriki": entity_stats["doriki"],
                    "busoshoku_haki": haki_data["busoHakiExp"],
                    "kenboshoku_haki": haki_data["kenHakiExp"],
                    "haoshoku_haki": haoshoku,
                    "haki_limit": round(2400 + (total_haki * 120), 1),
                    "devil_fruits": devil_fruits,
                    "eaten_devil_fruits": eaten_devil_fruits,
                    "inventory_devil_fruits": inventory_devil_fruits,
                    "abilities": ability_data["unlocked_abilities"],
                },
            )
            if player_db := await Player.find_one(Player.uuid == uuid):
                player_entry.id = player_db.id
                player_entry.user = player_db.user
                if player_db != player_entry:
                    await player_entry.replace()
            else:
                self.bot.logger.info(f"New player found - {player_entry.name}")
                await player_entry.insert()
            self.bot.dispatch("player_data_inserted", player_entry)

    @commands.Cog.listener("on_player_data_inserted")
    async def awakened_fruits(self, player):
        online_players = self.get_online_players()
        if online_players is None:
            return
        if player.name not in online_players:
            return
        awakened_abilities = load(Path("data/awakenings.json").open())
        player_abilities = [a.id for a in player.stats.abilities]
        for fruit, abilities in awakened_abilities.items():
            if fruit in [df.qualified_name for df in player.stats.eaten_devil_fruits]:
                for ability in abilities:
                    if set(ability["required"]).issubset(set(player_abilities)):
                        for awarded_ability in ability["awarded"]:
                            if awarded_ability["name"] not in player_abilities:
                                cmds = [
                                    f"ability give mineminenomi:{awarded_ability['name']} {player.name}",
                                    f"msg {player.name} ??2you've unlocked ??4{ability['name']}??2 ability??r",
                                    "save-all",
                                ]
                                if not run_rcon_command(self.bot, cmds):
                                    return self.bot.logger.error("Failed to give ability.")
                                self.bot.logger.info(f"Gave {awarded_ability['name']} to {player.name}")
                    else:
                        for awarded_ability in ability["awarded"]:
                            if awarded_ability["name"] in player_abilities:
                                cmds = [
                                    f"ability remove mineminenomi:{awarded_ability['name']} {player.name}",
                                    "save-all",
                                ]
                                if not run_rcon_command(self.bot, cmds):
                                    return self.bot.logger.error("Failed to give ability.")
                                self.bot.logger.info(f"Removed {awarded_ability['name']} from {player.name}")
            else:
                for ability in abilities:
                    for awarded_ability in ability["awarded"]:
                        if awarded_ability["name"] in player_abilities:
                            if awarded_ability["fruit"] not in [
                                df.qualified_name for df in player.stats.eaten_devil_fruits
                            ]:
                                cmds = [
                                    f"ability remove mineminenomi:{awarded_ability['name']} {player.name}",
                                    "save-all",
                                ]
                                if not run_rcon_command(self.bot, cmds):
                                    return self.bot.logger.error("Failed to remove ability - No Fruit")
                                self.bot.logger.info(f"Removed {awarded_ability['name']} from {player.name} | No Fruit")

    @tasks.loop(minutes=1)
    async def manage_roles(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.bot.config.bot.server)
        for member in guild.members:
            player = await Player.find_one(Player.user.user_id == member.id, fetch_links=True)
            roles = {key: guild.get_role(value) for key, value in self.bot.config.mineminenomi.races.dict().items()}
            await self.manage_races(roles, member, player)
            roles = {key: guild.get_role(value) for key, value in self.bot.config.mineminenomi.factions.dict().items()}
            await self.manage_factions(roles, member, player)
            roles = {
                key: guild.get_role(value) for key, value in self.bot.config.mineminenomi.fighting_styles.dict().items()
            }
            await self.manage_fighting_styles(roles, member, player)

    async def manage_races(self, roles, member, player):
        for race, role in roles.items():
            if player and player.stats.race.value == race:
                if role not in member.roles:
                    await member.add_roles(role)
            else:
                if role in member.roles:
                    await member.remove_roles(role)

    async def manage_factions(self, roles, member, player):
        for faction, role in roles.items():
            if player and player.stats.faction.value == faction:
                if role not in member.roles:
                    await member.add_roles(role)
            else:
                if role in member.roles:
                    await member.remove_roles(role)

    async def manage_fighting_styles(self, roles, member, player):
        for fighting_style, role in roles.items():
            if player and player.stats.fighting_style.value == fighting_style:
                if role not in member.roles:
                    await member.add_roles(role)
            else:
                if role in member.roles:
                    await member.remove_roles(role)


async def setup(bot):
    await bot.add_cog(PlayerEvents(bot))
