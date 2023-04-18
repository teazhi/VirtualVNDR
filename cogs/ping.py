import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog, name="Ping"):
    """ | Single command to ping the bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Ping the bot")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("Pong!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))