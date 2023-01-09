import gzip
from pathlib import Path

from discord.ext import commands, tasks


class LogCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs_folder = Path("cache/logs")
        self.logs = {}
        self.read_logs.start()

    async def cog_unload(self):
        self.read_logs.cancel()

    def extract_logs(self):
        for log in list(self.logs_folder.iterdir()):
            if log.with_suffix("").exists():
                log.unlink()
                continue
            if log.suffix == ".gz":
                with gzip.open(log, "rb") as ff:
                    with open(log.with_suffix(""), "w+") as f:
                        logs = ff.read().decode("utf-8")
                        f.write(logs)
            elif log.suffix == ".log":
                self.logs[log.stem] = log.read_text().split("\n")

    @tasks.loop(seconds=30)
    async def read_logs(self):
        await self.bot.wait_until_ready()
        self.extract_logs()


async def setup(bot):
    await bot.add_cog(LogCommands(bot))
