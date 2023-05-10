import os
import discord
from discord.ui import Select, View
from discord.ext import commands
import stripe
from dotenv import load_dotenv
from discord import app_commands
import config

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

    @commands.command(description="Work in progress status")
    async def wip(self, ctx):
        emb = discord.Embed(
            title=f'Currently Working On:', color=discord.Color.from_rgb(210, 43, 43),
            description=f"",
        )
        emb.add_field(name="__                                        __", value="", inline=False)
        emb.add_field(name="Internal", value=">>> • Finishing Stripe API implementation\n• Adding other payment methods\n   • Paypal\n   • Cashapp\n• Ticket system", inline=False)
        emb.add_field(name="External", value=">>> • Landing site\n• Update github\n• Documentation page", inline=False)
        emb.add_field(name="__                                        __", value="", inline=False)
        config.SET_EMBED_FOOTER(self, emb)
        await ctx.send(embed=emb)


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))