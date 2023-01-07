from discord.ext import commands, tasks
from utils.database.models.mineminenomi import Player
from utils.mineminenomi import int_array_to_uuid
from json import load
from pathlib import Path
from datetime import datetime
from data.models.devil_fruit import FruitStatus


class PlayerEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.manage_roles.start()

    @commands.Cog.listener("on_player_data_read")
    async def on_player_data_read(self, data):
        username_cache = load(Path('cache/game/usernamecache.json').open())
        for player in data:
            uuid = int_array_to_uuid(player['UUID'])
            haki_data = player['ForgeCaps']['mineminenomi:haki_data']
            devil_fruit = player['ForgeCaps']['mineminenomi:devil_fruit']
            entity_stats = player['ForgeCaps']['mineminenomi:entity_stats']
            ability_data = player['ForgeCaps']['mineminenomi:ability_data']
            total_haki = haki_data['busoHakiExp'] + haki_data['kenHakiExp']
            eaten_devil_fruits = [
                df
                for df in self.bot.devil_fruits
                if df.qualified_name == devil_fruit['devilFruit'] or devil_fruit['hasYamiPower']
            ]
            inventory_devil_fruits = [
                df
                for item in player['Inventory']
                for df in self.bot.devil_fruits
                if df.name == item['id'].split(':')[1]
            ]
            devil_fruits = eaten_devil_fruits + inventory_devil_fruits
            haoshoku = False
            for ability in ability_data['unlocked_abilities']:
                if ability['id'] == "mineminenomi:haoshoku_haki":
                    haoshoku = True
            player_entry = Player(
                uuid=uuid,
                name=username_cache.get(str(uuid), "Unknown"),
                last_update=datetime.utcnow(),
                stats={
                    "race": entity_stats['race'],
                    "sub_race": entity_stats['subRace'],
                    "faction": entity_stats['faction'],
                    "fighting_style": entity_stats['fightingStyle'],
                    "inventory": player['Inventory'],
                    "belly": entity_stats['belly'],
                    "bounty": entity_stats['bounty'],
                    "loyalty": entity_stats['loyalty'],
                    "doriki": entity_stats['doriki'],
                    "busoshoku_haki": haki_data['busoHakiExp'],
                    "kenboshoku_haki": haki_data['kenHakiExp'],
                    "haoshoku_haki": haoshoku,
                    "haki_limit": round(2200 + (total_haki * 32), 1),
                    "devil_fruits": devil_fruits,
                    "eaten_devil_fruits": eaten_devil_fruits,
                    "inventory_devil_fruits": inventory_devil_fruits
                }
            )
            if player_entry.stats.haoshoku_haki:
                print(player_entry.name)
            #print([df.mod_data.status for df in self.bot.devil_fruits if df.mod_data.status != FruitStatus.lost])
            if player_db := await Player.find_one(Player.uuid == uuid):
                player_entry.id = player_db.id
                await player_entry.replace()
            else:
                await player_entry.insert()

    @tasks.loop(minutes=1)
    async def manage_roles(self):
        await self.bot.modules_ready()
        guild = self.bot.get_guild(self.bot.config.bot.server)
        await self.manage_races(guild)

    async def manage_races(self, guild):
        roles = {
            key: guild.get_role(value)
            for key, value in self.bot.config.mineminenomi.races.json().items()
        }
        async for player in Player.find_many():
            for race, role in roles.items():
                if Player.stats.race.name == race:
                    ... # Missing logic
                else:
                    ... # Missing logic


async def setup(bot):
    await bot.add_cog(PlayerEvents(bot))
