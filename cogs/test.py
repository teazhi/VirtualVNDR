import os
import discord
from discord.ui import Select, View
from discord.ext import commands
import stripe
from dotenv import load_dotenv
from discord import app_commands

class Test(commands.Cog, name="Test"):
    """ | Command for testing purposes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    load_dotenv()

    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        customers = stripe.Customer.list()

        if len(customers) == 0:
            print("No customers")
        else:
            print("there are customers")

        await interaction.response.send_message("Test command is working.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))