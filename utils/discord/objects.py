from discord import ui, Interaction, ButtonStyle


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