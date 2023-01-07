from discord.ext import commands
from utils.database.models.mineminenomi import Player
from utils.mineminenomi import int_array_to_uuid
from json import load
from pathlib import Path
from datetime import datetime


class PlayerEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_player_data_read")
    async def on_player_data_read(self, data):
        username_cache = load(Path('cache/game/usernamecache.json').open())
        for player in data:
            uuid = int_array_to_uuid(player['UUID'])
            haki_data = player['ForgeCaps']['mineminenomi:haki_data']
            devil_fruit = player['ForgeCaps']['mineminenomi:devil_fruit']
            entity_stats = player['ForgeCaps']['mineminenomi:entity_stats']
            total_haki = haki_data['busoHakiExp'] + haki_data['kenHakiExp']
            eaten_devil_fruits = [
                df
                for df in self.bot.devil_fruits
                if df.qualified_name == devil_fruit['devilFruit'] or devil_fruit['hasYamiPower']
            ]
            inventory_devil_fruits = []
            devil_fruits = eaten_devil_fruits + inventory_devil_fruits
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
                    "haoshoku_haki": False,
                    "haki_limit": round(2200 + (total_haki * 32), 1),
                    "devil_fruits": devil_fruits,
                    "eaten_devil_fruits": eaten_devil_fruits,
                    "inventory_devil_fruits": inventory_devil_fruits
                }
            )
            if player_db := await Player.find_one(Player.uuid == uuid):
                player_entry.id = player_db.id
                await player_entry.replace()
            else:
                await player_entry.insert()


async def setup(bot):
    await bot.add_cog(PlayerEvents(bot))
