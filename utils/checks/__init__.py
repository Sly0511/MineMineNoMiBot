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
