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

        checkoutsessions = stripe.checkout.Session.list()

        emb = discord.Embed(title="All checkout sessions")

        for sesh in checkoutsessions:
            emb.add_field(name=sesh.id, value=sesh.url)

        await interaction.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name="expirecheckout")
    async def expireCheckout(self, interaction: discord.Interaction):
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        checkoutsessions = stripe.checkout.Session.list()

        for sesh in checkoutsessions:
            stripe.checkout.Session.expire(sesh.id)

        emb = discord.Embed(title="All checkout sessions have been expired.")

        await interaction.response.send_message(embed=emb, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))