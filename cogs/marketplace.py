import os
import discord
from discord.ext import commands
import config
import asyncio
import datetime
from discord.ui import Select, View
from discord.ext.commands import has_permissions, MissingPermissions
from discord import app_commands
import json
import stripe
from dotenv import load_dotenv

class Marketplace(commands.Cog, name="Marketplace"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    load_dotenv()

    def load_mpItems(self, pathToFile):
        if os.path.getsize(pathToFile) > 0:
            with open(pathToFile) as fp:
                return json.load(fp)
            
    def checkAdminPermissions(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return False
        else:
            return True

    
    # ——————————————————————————————————————
    # SHOP COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="Display current available products in the marketplace")
    async def shop(self, interaction: discord.Interaction):
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')
        mpItems = self.load_mpItems(MPFILEPATH)
        
        mpEmbed = discord.Embed(
            title=":moneybag: Marketplace :moneybag:",
            description="Browse available products in the marketplace.",
            color = config.MAIN_COLOR,
        )

        if len(mpItems) == 0:
            mpEmbed.add_field(
                name="\u200b",
                value="There are no products to display currently.",
                inline=False
            )
        else:
            for product in mpItems.values():
                mpEmbed.add_field(
                    name=f"__                                                           __\
                        \n\n{product[0]}",
                    value=f">>> **Price:** ${product[3]/100:,.2f}\n**Qty:** {product[2]}\n**Description:**\n{product[1]}\n\
                        __                                                           __",
                    inline=True
                )

        config.SET_EMBED_FOOTER(self, mpEmbed)


        # PURCHASE BUTTON
        purchaseBTN = discord.ui.Button(label="Purchase", style=discord.ButtonStyle.green, emoji="💳")

        async def pBTNCallback(interaction):
            emb = discord.Embed(
                title="Select a product to purchase:",
                description="",
                color = config.MAIN_COLOR
            )
        
            select = Select()

            prodID = ""
            prodQty = 0

            for product in mpItems.values():
                prodID = product[4]
                prodQty = product[2]
                select.options.append(discord.SelectOption(label=f"{product[0]} | ID: {prodID}" , description=product[1]))

            async def createCheckoutCallback(interaction):
                findIDinStr = list(select.values[0].split(" "))

                await interaction.response.defer()
                emb = discord.Embed(title="Attempting to find product...")
                newmsg = await interaction.followup.send(embed=emb)

                for price in stripe.Price.list():
                    if price.product == findIDinStr[len(findIDinStr)-1]:
                        await asyncio.sleep(1)
                        emb = discord.Embed(title="Product found.")
                        await newmsg.edit(embed=emb)
                        await asyncio.sleep(1.5)
                        embed = discord.Embed(title="Create a checkout link?")
                        createCOLinkBTN = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green, emoji="✅")

                        async def createCOCallback(interaction):
                            stripe.Product.retrieve(price.product)
                            checkoutSesh = stripe.checkout.Session.create(
                                success_url="https://virtualvndr.com/success?id={CHECKOUT_SESSION_id}",
                                mode="payment",
                                line_items=[
                                    {
                                        "price": price.id,
                                        "adjustable_quantity": {"enabled": True, "minimum": 1, "maximum": prodQty},
                                        "quantity": 1
                                    }
                                ]
                            )
                            await interaction.user.send(f"Created checkout session! {checkoutSesh.url}")
                        
                        createCOLinkBTN.callback = createCOCallback
                        createCOLinkBTNView = discord.ui.View()
                        createCOLinkBTNView.add_item(createCOLinkBTN)
                        await newmsg.edit(embed=embed, view=createCOLinkBTNView)
            
            select.callback = createCheckoutCallback

            view = View()
            view.add_item(select)
            purchaseBTNView.remove_item(purchaseBTN)
            await interaction.response.defer()
            await interaction.user.send(embed=mpEmbed, view=purchaseBTNView)
            await interaction.user.send(embed=emb, view=view)

        purchaseBTN.callback = pBTNCallback

        purchaseBTNView = discord.ui.View()
        purchaseBTNView.add_item(purchaseBTN)

        #-------------------------------------------
        
        # PURCHASE DROPDOWN
        if len(mpItems) != 0:
            await interaction.response.send_message(embed=mpEmbed, view=purchaseBTNView, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mpEmbed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Marketplace(bot))