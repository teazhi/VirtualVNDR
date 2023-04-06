import os
import discord
from discord.ext import commands
import config
import asyncio
import datetime
from discord.ui import Select, View
import json

class Marketplace(commands.Cog, name="Marketplace"):
    """ | List of all marketplace commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Display current available items in the marketplace")
    async def shop(self, ctx: commands.Context):
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if os.path.getsize(mpFilePath) > 0:
            with open(mpFilePath) as fp:
                mpItems = json.load(fp)
        
        emb = discord.Embed(
            title=f":moneybag: Marketplace :moneybag:",
            description=f"Browse available items in the marketplace.",
            color = discord.Color.from_rgb(210, 43, 43),
        )
        emb.add_field(name="", value="", inline=False)
        if len(mpItems) == 0:
            emb.add_field(name="", value="There are no products to display currently.", inline=False)
        else:
            for item in mpItems.values():
                emb.add_field(name=f"{item[0]} | `QTY: {item[2]}`", value=f"{item[1]}", inline=False)

        emb.add_field(name="", value="", inline=False)

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} is in development by {config.OWNER_NAME}', icon_url=config.LOGO_URL)

        await ctx.send(embed=emb)
        
        # PURCHASE DROPDOWN
        emb = discord.Embed(title="Select a product to purchase:", description="", color = discord.Color.from_rgb(210, 43, 43))
        
        select = Select()

        for item in mpItems.values():
            select.options.append(discord.SelectOption(label=f"{item[0]} | QTY: {item[2]}" , description=item[1]))

        async def doSmthCallback(interation):
            await interation.response.send_message(f"You chose: {select.values}")
        
        select.callback = doSmthCallback

        view = View()
        view.add_item(select)

        await ctx.send(embed=emb, view=view)

    @commands.command(description="Add a product to the marketplace", usage=" [ITEM_ID]")
    async def addproduct(self, ctx: commands.Context, itemID = None):
        global mpItems
        mpItems = {} #marketplace items
        global productDetails
        productDetails = []

        productDetails.clear()
        if itemID == None:
            emb = discord.Embed(title=f'Error', description=f"Please provide an item id. \n\n`Usage: {config.PREFIX}addproduct [ITEM_ID]`",
                                        color=discord.Color.red())
            await ctx.send(embed=emb)
        else:
            await ctx.send(f"Creating a new product with item ID `{itemID}`...")

            await ctx.send("Begin by providing an item name:")
            
            def checkAuthorAndChannel(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            try:
                itemName = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you didn't reply in time! Please try again, but reply within 30 seconds.")
                return

            await ctx.send("Item description:")

            try:
                itemDesc = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("Sorry, you didn't reply in time! Please try again, but reply within 30 seconds.")
                return

            while True:
                await ctx.send("Item quantity:")

                try:
                    itemQuantity = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                    if (str(itemQuantity.content)).isnumeric():
                        break
                    else:
                        await ctx.send("Please provide a number.")
                        continue
                except asyncio.TimeoutError:
                    await ctx.send("Sorry, you didn't reply in time! Please try again, but reply within 30 seconds.")
                    return
            
            itemName = str(itemName.content)
            itemDesc = str(itemDesc.content)
            itemQuantity = str(itemQuantity.content)

            if itemName.lower() == 'cancel' or itemDesc.lower() == 'cancel' or itemQuantity.lower() == 'cancel':
                await ctx.send("Process has been terminated.")
                return
            
            productDetails.append(itemName)
            productDetails.append(itemDesc)
            productDetails.append(itemQuantity)

            mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

            if os.path.getsize(mpFilePath) > 0:
                with open(mpFilePath) as fp:
                    mpItems = json.load(fp)
                mpItems.update({itemID: productDetails})
            else:
                mpItems[itemID] = productDetails

            with open(mpFilePath, 'w') as json_file:
                json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))

            embed = discord.Embed(title=f'Item Details | `id: {itemID}`', description="",
                                        color=discord.Color.green())
            embed.add_field(name="Name:", value=itemName, inline=False)
            embed.add_field(name="Description:", value=itemDesc, inline=False)
            embed.add_field(name="Quantity:", value=itemQuantity, inline=False)

            embed.add_field(name="", value="", inline=False)

            itemNumber = len(mpItems)
            embed.add_field(name="", value=f"`Inventory Item #: {itemNumber}`", inline=False)

            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} is in development by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
            await ctx.send(embed=embed)

    @commands.command(description="Remove a product from the marketplace", usage=" [ITEM_ID]")
    async def removeproduct(self, ctx: commands.Context, itemID = None):
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if itemID is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide an item id. \n\n`Usage: {config.PREFIX}removeproduct [ITEM_ID]`",
                                        color=discord.Color.red())
            await ctx.send(embed=emb)
        else:
            if os.path.getsize(mpFilePath) > 0:
                with open(mpFilePath) as fp:
                    mpItems = json.load(fp)

            if itemID in mpItems:
                del mpItems[itemID]

                with open(mpFilePath, 'w') as json_file:
                    json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))
                    
                emb = discord.Embed(title=f'Success', description=f"`{itemID}` has been removed from the marketplace.",
                                        color=discord.Color.green())
            else:
                emb = discord.Embed(title=f'Error', description=f"`{itemID}` is not a valid item ID.",
                                        color=discord.Color.red())
            
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} is in development by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
        await ctx.send(embed=emb)

    @commands.command(description="List all products and their IDs")
    async def listproductids(self, ctx: commands.Context):
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if os.path.getsize(mpFilePath) > 0:
            with open(mpFilePath) as fp:
                mpItems = json.load(fp)

        embed = discord.Embed(title=f"Product ID's", description="",
                              color=discord.Color.from_rgb(210, 43, 43))

        for item in mpItems:
            itemname = mpItems[item][0]
            embed.add_field(name=f"{itemname} - `ID: {item}`", value="", inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} is in development by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Marketplace(bot))