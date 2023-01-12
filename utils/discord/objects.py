from discord import ButtonStyle, Interaction, ui

from utils.database.models import User
from utils.database.models.mineminenomi import Player


class Traceback(ui.View):
    def __init__(self, ctx, exception, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.exception = exception

    @ui.button(label="Show Traceback", style=ButtonStyle.grey)
    async def show(self, interaction: Interaction, button: ui.Button):
        if len(self.exception) > 2000:
            await interaction.response.send_message(
                f"```py\n{self.exception[:1990]}```", ephemeral=True
            )
            await interaction.followup.send(
                f"```py\n{self.exception[1990:3980]}```", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"```py\n{self.exception}```", ephemeral=True
            )


class InsertCodeModal(ui.Modal, title="Code Input"):
    sent_code = ui.TextInput(
        label="Input the code that you were sent in-game",
        min_length=4,
        max_length=4,
        placeholder="1234",
    )

    def __init__(self, bot, player, code: int):
        super().__init__()
        self.bot = bot
        self.player = player
        self.code = code

    async def on_submit(self, interaction) -> None:
        try:
            if int(self.sent_code.value) != self.code:
                raise Exception("Wrong!")
            user = await User.find_one(User.user_id == interaction.user.id)
            player = await Player.find_one(Player.user == user.to_ref())
            if player is not None:
                return await interaction.response.send_message(
                    "You have already linked your discord account."
                )
            player = await Player.find_one(Player.name == self.player)
            if not player:
                return await interaction.response.send_message("Player not found.")
            if player.user is not None:
                return await interaction.response.send_message(
                    "This player already has a discord account linked."
                )
            player.user = user
            await player.save()
            await interaction.response.send_message("Player linked to discord account.")
        except ValueError:
            return await interaction.response.send_message(
                "The value input was not correct."
            )


class CodeButton(ui.View):
    def __init__(self, bot, user, player, code):
        super().__init__()
        self.bot = bot
        self.user = user
        self.player = player
        self.code = code

    async def interaction_check(self, interaction):
        if self.user.id != interaction.user.id:
            await interaction.response.send_message(
                "You can't interact with this button.", ephemeral=True
            )
            return False
        return True

    @ui.button(label="Input code", style=ButtonStyle.green)
    async def submit_code(self, interaction, button):
        await interaction.response.send_modal(
            InsertCodeModal(self.bot, self.player, self.code)
        )
        self.stop()
