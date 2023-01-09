from discord import app_commands
from discord.ext import commands


def in_bot_owners():
    def predicate(ctx) -> bool:
        if ctx.author.id in ctx.bot.config.bot.owners:
            return True
        return False

    return commands.check(predicate)


def in_bot_admins():
    def predicate(ctx) -> bool:
        if ctx.author.id in ctx.bot.config.bot.admins + ctx.bot.config.bot.owners:
            return True
        return False

    return commands.check(predicate)


def is_bot_owners_interaction():
    def predicate(interaction) -> bool:
        if interaction.user.id in interaction.client.config.bot.owners:
            return True
        return False

    return app_commands.check(predicate)
