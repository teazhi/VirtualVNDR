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
    """ | List of all marketplace commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    load_dotenv()

    def load_mpItems(self, pathToFile):
        if os.path.getsize(pathToFile) > 0:
            with open(pathToFile) as fp:
                return json.load(fp)
    
    # ——————————————————————————————————————
    # SHOP COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="Display current available products in the marketplace")
    async def shop(self, interaction: discord.Interaction):
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
                    name=f"{product[0]} | `QTY: {product[2]}`",
                    value=f"{product[1]}",
                    inline=False
                )

        config.SET_EMBED_FOOTER(self, mpEmbed)
        
        # PURCHASE DROPDOWN
        if len(mpItems) != 0:
            emb = discord.Embed(
                title="Select a product to purchase:",
                description="",
                color = config.MAIN_COLOR
            )
        
            select = Select()

            for product in mpItems.values():
                select.options.append(discord.SelectOption(label=f"{product[0]} | QTY: {product[2]}" , description=product[1]))

            async def doSmthCallback(interact):
                await interact.response.send(f"You chose: {select.values}")
            
            select.callback = doSmthCallback

            view = View()
            view.add_item(select)

            await interaction.response.send_message(embed=mpEmbed, ephemeral=True)
            await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=mpEmbed, ephemeral=True)

    # ——————————————————————————————————————
    # ADDPRODUCT COMMAND
    # ——————————————————————————————————————
    @commands.command(description="Add a product to the marketplace", usage=" [PROD_ID]", aliases=["ap"])
    @has_permissions(administrator=True)
    async def addproduct(self, ctx: commands.Context, productID = None, *arg):
        if len(arg) > 0:
            embed = discord.Embed(
                title="Invalid Arguments",
                description=f"Add product only asks for one argument: `PROD_ID`",
                color=config.ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return

        def process_cancelled():
            embed = discord.Embed(
                title="Process Cancelled",
                description="You have cancelled the process of creating a new product.",
                color=config.SUCCESS_COLOR
            )
            return embed
        
        def process_terminated():
            embed = discord.Embed(
                title="Process Terminated",
                description="Sorry, you didn't reply in time! Please try again.",
                color=config.ERROR_COLOR
            )
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
        
        def printItemDetails(self, productID, productName, productDesc, productPPU, productQuantity, mpItems):
            embed = discord.Embed(
                title=f'Item Details | `id: {productID}`', description="",
                color=config.SUCCESS_COLOR
            )
            embed.add_field(name="Name:", value=productName, inline=False)
            embed.add_field(name="Description:", value=productDesc, inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="Price Per Unit:", value=productPPU, inline=True)
            embed.add_field(name="Quantity:", value=productQuantity, inline=True)

            embed.add_field(name="", value="", inline=False)

            productNumber = len(mpItems)
            embed.add_field(
                name="",
                value=f"`Updated!\nItems in Inventory: {productNumber}`",
                inline=False
            )

            config.SET_EMBED_FOOTER(self, embed)
            return embed
        
        global mpItems
        mpItems = {} # marketplace products
        global productDetails
        productDetails = []
        
        # STRIPE API KEY
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        # Marketplace File Path
        MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        productDetails.clear()

        mpItems = self.load_mpItems(MPFILEPATH)

        if productID in mpItems:
            emb = discord.Embed(
                title=f'There is already a product with ID: `{productID}`',
                description=f"Please try again.",
                color=config.ERROR_COLOR
            )
            await ctx.send(embed=emb)
            return
        
        for product in stripe.Product.list():
            if product.id== productID:
                emb = discord.Embed(
                    title=f'There is already a product with this ID archived in your Stripe store.',
                    description=f"Please remove `{product.name}` from your store and try again.\n\
                        [Head Over](https://dashboard.stripe.com/products?active=false)",
                    color=config.ERROR_COLOR
                )
                await ctx.send(embed=emb)
                return

        if productID == None:
            emb = discord.Embed(
                title=f'Error',
                description=f"Please provide a product id. \n\n`Usage: {config.PREFIX}addproduct [PROD_ID]`",
                color=config.ERROR_COLOR
            )
            await ctx.send(embed=emb)
        else:
            emb = discord.Embed(
                title=f"Creating a new product with product ID: `{productID}`", 
                description="**Please do not leave or chat during this process.**\n\
                            If you'd like to cancel the process at any time, please type `cancel`.\n\n\
                            You have **30 seconds** between each prompt to give an answer before the process is terminated.\n\n\
                            Starting soon..",
                color=config.MAIN_COLOR
            )
            await ctx.send(embed=emb)

            await asyncio.sleep(2.5)

            emb = discord.Embed(
                title=f"Begin by providing a product name:", 
                description="",
                color=config.MAIN_COLOR
            )
            await ctx.send(embed=emb)
            
            def checkAuthorAndChannel(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            
            try:
                productName = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                productName = str(productName.content)

                if productName.lower() == 'cancel':
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
                productDesc = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                productDesc = str(productDesc.content)
                if productDesc.lower() == 'cancel':
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
                    productQuantity = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                    productQuantity = str(productQuantity.content)
                    if productQuantity.lower() == 'cancel':
                        await ctx.send(embed=process_cancelled())
                        return
                    if productQuantity.isnumeric():
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
                    productPPU = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                    productPPU = str(productPPU.content)
                    if productPPU.lower() == 'cancel':
                        await ctx.send(embed=process_cancelled())
                        return
                    if productPPU.isnumeric():
                        productPPU = int(productPPU)
                        break
                    elif is_float(productPPU):
                        await ctx.send(embed=provide_int_val())
                        continue
                    else:
                        await ctx.send(embed=invalid_number())
                        continue
                except asyncio.TimeoutError:
                    await ctx.send(embed=process_terminated())
                    return
            
            productDetails.append(productName)
            productDetails.append(productDesc)
            productDetails.append(productQuantity)
            # productPPU = productPPU*100
            productDetails.append(productPPU)

            stripe.Product.create(id=productID, name=productName, description=productDesc)
            newProductPrice = stripe.Price.create(
                product=productID,
                unit_amount=productPPU,
                currency="usd"
            )

            # newProductSession = stripe.checkout.Session.create(
            #     line_items=[
            #         {
            #             "price_data": newProductPrice,
            #             "adjustable_quantity": {"enabled": True, "minimum": 1, "maximum": productQuantity},
            #             "quantity": 1,
            #         },
            #     ],
            #     automatic_tax={"enabled": True},
            #     mode="payment",
            #     success_url="https://example.com/success",
            #     cancel_url="https://example.com/cancel",
            # )

            # if os.path.getsize(mpFilePath) > 0:
            #     mpItems.update({productID: productDetails})
            # else:
            mpItems[productID] = productDetails

            with open(MPFILEPATH, 'w') as json_file:
                json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))

            await ctx.send(embed=printItemDetails(self, productID, productName, productDesc, productPPU, productQuantity, mpItems))

    # ——————————————————————————————————————
    # REMOVEPRODUCT COMMAND
    # ——————————————————————————————————————
    @commands.command(description="Remove a product from the marketplace", usage=" [PROD_ID]", aliases=["rp"])
    @has_permissions(administrator=True)
    async def removeproduct(self, ctx: commands.Context, productID = None, *arg):
        MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        if len(arg) > 0:
            embed = discord.Embed(
                title="Invalid Arguments",
                description=f"Remove product only asks for one argument: `PROD_ID`",
                color=config.ERROR_COLOR
            )
            await ctx.send(embed=embed)
            return

        stripe.api_key = os.getenv("STRIPE_API_KEY")

        if productID is None:
            emb = discord.Embed(
                title=f'Error',
                description=f"Please provide a product id. \n\n`Usage: {config.PREFIX}removeproduct [PROD_ID]`",
                color=config.ERROR_COLOR
            )
            await ctx.send(embed=emb)
            return
        else:
            mpItems = self.load_mpItems(MPFILEPATH)

            if productID in mpItems:
                findProd = stripe.Product.retrieve(productID)
                findProd.modify(productID, active="false")

                del mpItems[productID]

                with open(MPFILEPATH, 'w') as json_file:
                    json.dump(mpItems, json_file, 
                                    indent=4,  
                                    separators=(',',': '))
                    
                emb = discord.Embed(
                    title=f'Success',
                    description=f"`{productID}` has been removed from the marketplace, but is \nstill archived in your Stripe database.\n\n\
                                Head over to your [Stripe dashboard](https://dashboard.stripe.com/products?active=false) to delete it permanently.",
                    color=config.SUCCESS_COLOR
                )
            else:
                emb = discord.Embed(
                    title=f'Error',
                    description=f"`{productID}` is not a valid product ID.",
                    color=config.ERROR_COLOR
                )
            
        config.SET_EMBED_FOOTER(self, emb)
        await ctx.send(embed=emb)

    # ——————————————————————————————————————
    # LISTPRODUCTIDS COMMAND
    # ——————————————————————————————————————
    @commands.command(description="List all products and their IDs", aliases=["lpids"])
    @has_permissions(administrator=True)
    async def listproductids(self, ctx: commands.Context):
        MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')
        mpItems = self.load_mpItems(MPFILEPATH)

        embed = discord.Embed(
            title=f"Product ID's", description="",
            color=config.MAIN_COLOR
        )

        if len(mpItems) > 0:
            for product in mpItems:
                productname = mpItems[product][0]
                embed.add_field(name=f"{productname} - `ID: {product}`", value="", inline=False)
        else:
            embed.add_field(name="", value=f"There are no products in your marketplace.\n\nAdd a product using: `{config.PREFIX}addproduct [PROD_ID]`", inline=False)

        config.SET_EMBED_FOOTER(self, embed)
        await ctx.send(embed=embed)
    
    # ——————————————————————————————————————
    # LISTARCHIVED COMMAND
    # ——————————————————————————————————————
    @commands.command(description="List all products and their IDs", aliases=["larchived"])
    @has_permissions(administrator=True)
    async def listarchived(self, ctx: commands.Context):
        stripe.api_key = os.getenv("STRIPE_API_KEY")

        embed = discord.Embed(
            title=f"Archived Products", description="",
            color=config.MAIN_COLOR
        )

        if len(stripe.Product.list(active="false")) > 0:
            for product in stripe.Product.list(active="false"):
                productname = product.name
                embed.add_field(name=f"{productname} - `ID: {product.id}`", value="", inline=False)
        else:
            embed.add_field(name="", value="There are no products archived.", inline=False)

        config.SET_EMBED_FOOTER(self, embed)
        await ctx.send(embed=embed)

    
    @addproduct.error
    @removeproduct.error
    @listproductids.error
    @listarchived.error
    async def admin_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            emb = discord.Embed(title=f'Sorry {ctx.message.author}!', description="You do not have permissions to do that.",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Marketplace(bot))