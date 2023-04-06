import os
import discord
from discord.ext import commands
import config
import asyncio
import datetime
from discord.ui import Select, View
import json
import stripe
from dotenv import load_dotenv

class Marketplace(commands.Cog, name="Marketplace"):
    """ | List of all marketplace commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    load_dotenv()

    @commands.command(description="Display current available items in the marketplace", aliases=["mp", "marketplace"])
    async def shop(self, ctx: commands.Context):
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if os.path.getsize(mpFilePath) > 0:
            with open(mpFilePath) as fp:
                mpItems = json.load(fp)
        
        emb = discord.Embed(
            title=":moneybag: Marketplace :moneybag:",
            description="Browse available items in the marketplace.",
            color = config.MAIN_COLOR,
        )
        if len(mpItems) == 0:
            emb.add_field(name="\u200b", value="There are no products to display currently.", inline=False)
        else:
            for item in mpItems.values():
                emb.add_field(name=f"{item[0]} | `QTY: {item[2]}`", value=f"{item[1]}", inline=False)

        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} | by {config.OWNER_NAME}', icon_url=config.LOGO_URL)

        await ctx.send(embed=emb)
        
        # PURCHASE DROPDOWN
        emb = discord.Embed(title="Select a product to purchase:", description="", color = config.MAIN_COLOR)
        
        select = Select()

        for item in mpItems.values():
            select.options.append(discord.SelectOption(label=f"{item[0]} | QTY: {item[2]}" , description=item[1]))

        async def doSmthCallback(interaction):
            await interaction.response.send(f"You chose: {select.values}")
        
        select.callback = doSmthCallback

        view = View()
        view.add_item(select)

        await ctx.send(embed=emb, view=view)

    @commands.command(description="Add a product to the marketplace", usage=" [ITEM_ID]", aliases=["ap"])
    async def addproduct(self, ctx: commands.Context, itemID = None, *arg):
        if len(arg) > 0:
            embed = discord.Embed(title="Invalid Arguments", description=f"Add product only asks for one argument: `ITEM_ID`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=embed)
            return

        def process_cancelled():
            embed = discord.Embed(title="Process Cancelled", description="You have cancelled the process of creating a new product.",
                                        color=config.SUCCESS_COLOR)
            return embed
        
        def process_terminated():
            embed = discord.Embed(title="Process Terminated", description="Sorry, you didn't reply in time! Please try again.",
                                        color=config.ERROR_COLOR)
            return embed
        
        def invalid_number():
            emb = discord.Embed(
                title=f"Invalid Number", 
                description="Please provide a number.",
                color=config.ERROR_COLOR
            )
            return emb
        
        def provide_int_val():
            emb = discord.Embed(
                title=f"Invalid Number", 
                description="Please provide an integer value.\nEx) 500 = $5.00",
                color=config.ERROR_COLOR
            )
            return emb
        
        def printItemDetails(self, itemID, itemName, itemDesc, itemPPU, itemQuantity, mpItems):
            embed = discord.Embed(title=f'Item Details | `id: {itemID}`', description="",
                                        color=config.SUCCESS_COLOR)
            embed.add_field(name="Name:", value=itemName, inline=False)
            embed.add_field(name="Description:", value=itemDesc, inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="Price Per Unit:", value=itemPPU, inline=True)
            embed.add_field(name="Quantity:", value=itemQuantity, inline=True)

            embed.add_field(name="", value="", inline=False)

            itemNumber = len(mpItems)
            embed.add_field(name="", value=f"`Inventory Item #: {itemNumber}`", inline=False)

            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} | by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
            return embed
        

        global mpItems
        mpItems = {} #marketplace items
        global productDetails
        productDetails = []

        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        stripe.api_key = os.getenv("STRIPE_API_KEY")

        productDetails.clear()

        with open(mpFilePath) as fp:
            mpItems = json.load(fp)

        if itemID in mpItems:
            emb = discord.Embed(title=f'Error', description=f"There is already an item with ID: `{itemID}`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
            return

        if itemID == None:
            emb = discord.Embed(title=f'Error', description=f"Please provide an item id. \n\n`Usage: {config.PREFIX}addproduct [ITEM_ID]`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
        else:
            emb = discord.Embed(
                title=f"Creating a new product with item ID: `{itemID}`", 
                description="**Please do not leave or chat during this process.**\n\
                    If you'd like to cancel the process at any time, please type `cancel`.\n\n\
                    __You have 30 seconds between each prompt to give an answer before the process is terminated.__",
                color=config.MAIN_COLOR
            )
            await ctx.send(embed=emb)

            await asyncio.sleep(2)

            emb = discord.Embed(
                title=f"Begin by providing an item name:", 
                description="",
                color=config.MAIN_COLOR
            )
            await ctx.send(embed=emb)
            
            def checkAuthorAndChannel(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            try:
                itemName = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                itemName = str(itemName.content)

                if itemName.lower() == 'cancel':
                    await ctx.send(embed=process_cancelled())
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=process_terminated())
                return

            emb = discord.Embed(
                title=f"Item Description:", 
                description="",
                color=config.MAIN_COLOR
            )
            await ctx.send(embed=emb)

            try:
                itemDesc = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                itemDesc = str(itemDesc.content)
                if itemDesc.lower() == 'cancel':
                    await ctx.send(embed=process_cancelled())
                    return
            except asyncio.TimeoutError:
                await ctx.send(embed=process_terminated())
                return

            while True:
                emb = discord.Embed(
                    title=f"Item Quantity:", 
                    description="",
                    color=config.MAIN_COLOR
                )
                await ctx.send(embed=emb)

                try:
                    itemQuantity = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                    itemQuantity = str(itemQuantity.content)
                    if itemQuantity.lower() == 'cancel':
                        await ctx.send(embed=process_cancelled())
                        return
                    if itemQuantity.isnumeric():
                        break
                    else:
                        await ctx.send(embed=invalid_number())
                        continue
                except asyncio.TimeoutError:
                    await ctx.send(embed=process_terminated())
                    return
                
            def is_float(string):
                try:
                    float(string)
                    return True
                except ValueError:
                    return False
                
            while True:
                emb = discord.Embed(
                    title=f"Item Price/Unit (in hundreds):", 
                    description="`Ex) 500 = $5.00`",
                    color=config.MAIN_COLOR
                )
                await ctx.send(embed=emb)

                try:
                    itemPPU = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                    itemPPU = str(itemPPU.content)
                    if itemPPU.lower() == 'cancel':
                        await ctx.send(embed=process_cancelled())
                        return
                    if itemPPU.isnumeric():
                        itemPPU = int(itemPPU)
                        break
                    elif is_float(itemPPU):
                        await ctx.send(embed=provide_int_val())
                        continue
                    else:
                        await ctx.send(embed=invalid_number())
                        continue
                except asyncio.TimeoutError:
                    await ctx.send(embed=process_terminated())
                    return
            
            productDetails.append(itemName)
            productDetails.append(itemDesc)
            productDetails.append(itemQuantity)
            # itemPPU = itemPPU*100
            productDetails.append(itemPPU)

            stripe.Product.create(id=itemID, name=itemName, description=itemDesc)
            newProductPrice = stripe.Price.create(
                product=itemID,
                unit_amount=itemPPU,
                currency="usd"
            )

            # newProductSession = stripe.checkout.Session.create(
            #     line_items=[
            #         {
            #             "price_data": newProductPrice,
            #             "adjustable_quantity": {"enabled": True, "minimum": 1, "maximum": itemQuantity},
            #             "quantity": 1,
            #         },
            #     ],
            #     automatic_tax={"enabled": True},
            #     mode="payment",
            #     success_url="https://example.com/success",
            #     cancel_url="https://example.com/cancel",
            # )

            # if os.path.getsize(mpFilePath) > 0:
            #     mpItems.update({itemID: productDetails})
            # else:
            mpItems[itemID] = productDetails

            with open(mpFilePath, 'w') as json_file:
                json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))

            await ctx.send(embed=printItemDetails(self, itemID, itemName, itemDesc, itemPPU, itemQuantity, mpItems))

    @commands.command(description="Remove a product from the marketplace", usage=" [ITEM_ID]", aliases=["rp"])
    async def removeproduct(self, ctx: commands.Context, itemID = None, *arg):
        if len(arg) > 0:
            embed = discord.Embed(title="Invalid Arguments", description=f"Remove product only asks for one argument: `ITEM_ID`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=embed)
            return

        stripe.api_key = os.getenv("STRIPE_API_KEY")
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if itemID is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide an item id. \n\n`Usage: {config.PREFIX}removeproduct [ITEM_ID]`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
            return
        else:
            if os.path.getsize(mpFilePath) > 0:
                with open(mpFilePath) as fp:
                    mpItems = json.load(fp)

            if itemID in mpItems:
                findProd = stripe.Product.retrieve(itemID)
                findProd.modify(itemID, active="false")

                del mpItems[itemID]

                with open(mpFilePath, 'w') as json_file:
                    json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))
                    
                emb = discord.Embed(title=f'Success', description=f"`{itemID}` has been removed from the marketplace, but is \nstill archived in your Stripe database.\n\n\
                                                                    Head over to your [Stripe dashboard](https://dashboard.stripe.com/products?active=false) to remove the item from the database.",
                                        color=config.SUCCESS_COLOR)
            else:
                emb = discord.Embed(title=f'Error', description=f"`{itemID}` is not a valid item ID.",
                                        color=config.ERROR_COLOR)
            
        emb.timestamp = datetime.datetime.now()
        emb.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} | by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
        await ctx.send(embed=emb)

    @commands.command(description="List all products and their IDs", aliases=["lpids"])
    async def listproductids(self, ctx: commands.Context):
        mpFilePath = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if os.path.getsize(mpFilePath) > 0:
            with open(mpFilePath) as fp:
                mpItems = json.load(fp)

        embed = discord.Embed(title=f"Product ID's", description="",
                              color=config.MAIN_COLOR)

        for item in mpItems:
            itemname = mpItems[item][0]
            embed.add_field(name=f"{itemname} - `ID: {item}`", value="", inline=False)

        embed.timestamp = datetime.datetime.now()
        embed.set_footer(text=f'{self.bot.user.display_name} {config.BOT_VERSION} | by {config.OWNER_NAME}', icon_url=config.LOGO_URL)
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Marketplace(bot))