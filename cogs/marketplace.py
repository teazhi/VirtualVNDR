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
                        \n{product[0]}",
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

            for product in mpItems.values():
                select.options.append(discord.SelectOption(label=f"{product[0]} | ID: {product[4]}" , description=product[1]))

            async def createCheckoutCallback(interaction):
                findIDinStr = list(select.values[0].split(" "))

                await interaction.response.defer()
                emb = discord.Embed(title="Attempting to find product...")
                newmsg = await interaction.followup.send(embed=emb)

                for price in stripe.Price.list():
                    if price.product == findIDinStr[len(findIDinStr)-1]:
                        await asyncio.sleep(2)
                        emb = discord.Embed(title="Product found.")
                        await newmsg.edit(embed=emb)
                        embed = discord.Embed(title="Create a checkout link?")
                        createCOLinkBTN = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green, emoji="✅")

                        async def createCOCallback(interaction):
                            # stripe.Product.retrieve(price.product)
                            # stripe.checkout.Session.create(
                            #     success_url="https://virtualvndr.com/success?id={CHECKOUT_SESSION_id}",
                            #     automatic_payment_methods={'enabled': True},
                            #     mode="payment",
                            #     line_items=[
                            #         {
                            #             "price": price.id,
                            #             "quantity": productQuantity,
                            #         }
                            #     ]
                            # )
                            await interaction.user.send("Created checkout session!")
                        
                        createCOLinkBTN.callback = createCOCallback
                        createCOLinkBTNView = discord.ui.View()
                        createCOLinkBTNView.add_item(createCOLinkBTN)
                        await interaction.user.send(embed=embed, view=createCOLinkBTNView)
            
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

    # ——————————————————————————————————————
    # ADDPRODUCT COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="Add a product to the marketplace")
    async def addproduct(self, interaction: discord.Interaction, productid: str):
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
            embed = discord.Embed(
                title=f"Invalid Number", 
                description="Please provide a number.",
                color=config.ERROR_COLOR
            )
            return embed
        
        def provide_int_val():
            embed = discord.Embed(
                title=f"Invalid Number", 
                description="Please provide an integer value.\nEx) 500 = $5.00",
                color=config.ERROR_COLOR
            )
            return embed
        
        def info_provided_success(var: str):
            embed = discord.Embed(
                title=f"Successfully provided `{var}`", 
                description="",
                color=config.SUCCESS_COLOR
            )
            return embed
        
        def printItemDetails(self, productid, productName, productDesc, productPPU, productQuantity, mpItems):
            embed = discord.Embed(
                title=f'Item Details | `id: {productid}`', description="",
                color=config.SUCCESS_COLOR
            )
            embed.add_field(name="Name:", value=productName, inline=False)
            embed.add_field(name="Description:", value=productDesc, inline=False)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="Price Per Unit:", value=f"${productPPU/100:,.2f}", inline=True)
            embed.add_field(name="Quantity:", value=productQuantity, inline=True)

            embed.add_field(name="", value="", inline=False)

            productNumber = len(mpItems)
            embed.add_field(
                name="",
                value=f">>> Products in inventory has been updated!\nProducts: **{productNumber}**",
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

        if productid in mpItems:
            emb = discord.Embed(
                title=f'There is already a product with ID: `{productid}`',
                description=f"Please try again.",
                color=config.ERROR_COLOR
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return
        
        for product in stripe.Product.list():
            if product.id == productid:
                emb = discord.Embed(
                    title=f'There is already a product with this ID archived in your Stripe store.',
                    description=f"Please remove `{product.name}` from your store and try again.\n\
                        [Head Over](https://dashboard.stripe.com/products?active=false)",
                    color=config.ERROR_COLOR
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return

        emb = discord.Embed(
            title=f"Creating a new product with product ID: `{productid}`", 
            description="**Please do not leave or chat during this process.**\n\
                        If you'd like to cancel the process at any time, please type `cancel`.\n\n\
                        You have **30 seconds** between each prompt to give an answer before the process is terminated.\n\n\
                        Starting soon..",
            color=config.MAIN_COLOR
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)

        await asyncio.sleep(2.5)

        emb = discord.Embed(
            title=f"Begin by providing a product name:", 
            description="",
            color=config.MAIN_COLOR
        )
        pNameMSG = await interaction.followup.send(embed=emb, ephemeral=True)
        
        def checkAuthorAndChannel(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel
        
        try:
            productNameMSG = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
            productName = str(productNameMSG.content)
            await productNameMSG.delete()

            if productName.lower() == 'cancel':
                await pNameMSG.edit(embed=process_cancelled())
                return
            
            await pNameMSG.edit(embed=info_provided_success("Product Name"))
        except asyncio.TimeoutError:
            await pNameMSG.edit(embed=process_terminated())
            return

        emb = discord.Embed(
            title=f"Product Description:", 
            description="",
            color=config.MAIN_COLOR
        )
        pDescMSG = await interaction.followup.send(embed=emb, ephemeral=True)

        try:
            productDescMSG = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
            productDesc = str(productDescMSG.content)
            await productDescMSG.delete()

            lengthError = discord.Embed(
                title=f"Length Error | Process Terminated", 
                description="The description must be 100 characters or less. Please try again.",
                color=config.ERROR_COLOR
            )
            if len(productDesc) > 100:
                await pDescMSG.edit(embed=lengthError)
                return
            if productDesc.lower() == 'cancel':
                await pDescMSG.edit(embed=process_cancelled())
                return
            await pDescMSG.edit(embed=info_provided_success("Product Description"))
        except asyncio.TimeoutError:
            await interaction.followup.send(embed=process_terminated())
            return

        while True:
            emb = discord.Embed(
                title=f"Product Quantity:", 
                description="",
                color=config.MAIN_COLOR
            )
            pQuantityMSG = await interaction.followup.send(embed=emb, ephemeral=True)

            try:
                productQuantityMSG = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                productQuantity = str(productQuantityMSG.content)
                await productQuantityMSG.delete()

                if productQuantity.lower() == 'cancel':
                    await pQuantityMSG.edit(embed=process_cancelled())
                    return
                if productQuantity.isnumeric():
                    await pQuantityMSG.edit(embed=info_provided_success("Product Quantity"))
                    break
                else:
                    await pQuantityMSG.edit(embed=invalid_number())
                    await asyncio.sleep(3)
                    continue
            except asyncio.TimeoutError:
                await pQuantityMSG.edit(embed=process_terminated())
                return
            
        def is_float(string):
            try:
                float(string)
                return True
            except ValueError:
                return False
            
        while True:
            emb = discord.Embed(
                title=f"Product Price/Unit (in hundreds):", 
                description="`Ex) 100 = $1.00`",
                color=config.MAIN_COLOR
            )
            pPPUMSG = await interaction.followup.send(embed=emb, ephemeral=True)

            try:
                productPPUMSG = await self.bot.wait_for("message", check=checkAuthorAndChannel, timeout=30)
                productPPU = str(productPPUMSG.content)
                await productPPUMSG.delete()

                if productPPU.lower() == 'cancel':
                    await pPPUMSG.edit(embed=process_cancelled())
                    return
                if productPPU.isnumeric():
                    productPPU = int(productPPU)
                    await pPPUMSG.edit(embed=info_provided_success("Product PPU"))
                    break
                elif is_float(productPPU):
                    await pPPUMSG.edit(embed=provide_int_val())
                    continue
                else:
                    await pPPUMSG.edit(embed=invalid_number())
                    continue
            except asyncio.TimeoutError:
                await pPPUMSG.edit(embed=process_terminated())
                return
        
        productDetails.append(productName)
        productDetails.append(productDesc)
        productDetails.append(productQuantity)
        # productPPU = productPPU*100
        productDetails.append(productPPU)
        productDetails.append(productid)

        stripe.Product.create(id=productid, name=productName, description=productDesc)
        newProductPrice = stripe.Price.create(
            product=productid,
            unit_amount=productPPU,
            currency="usd"
        )

        # if os.path.getsize(mpFilePath) > 0:
        #     mpItems.update({productid: productDetails})
        # else:
        mpItems[productid] = productDetails

        with open(MPFILEPATH, 'w') as json_file:
            json.dump(mpItems, json_file, 
                                indent=4,  
                                separators=(',',': '))

        await interaction.followup.send(embed=printItemDetails(self, productid, productName, productDesc, productPPU, productQuantity, mpItems), ephemeral=True)

    # ——————————————————————————————————————
    # REMOVEPRODUCT COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="Remove a product from the marketplace")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeproduct(self, interaction: discord.Interaction, productid: str):
        MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

        stripe.api_key = os.getenv("STRIPE_API_KEY")

        mpItems = self.load_mpItems(MPFILEPATH)

        if productid in mpItems:
            findProd = stripe.Product.retrieve(productid)
            findProd.modify(productid, active="false")

            del mpItems[productid]

            with open(MPFILEPATH, 'w') as json_file:
                json.dump(mpItems, json_file, 
                                indent=4,  
                                separators=(',',': '))
                
            emb = discord.Embed(
                title=f'Success',
                description=f"`{productid}` has been removed from the marketplace, but is \nstill archived in your Stripe database.\n\n\
                            Head over to your [Stripe dashboard](https://dashboard.stripe.com/products?active=false) to delete it permanently.",
                color=config.SUCCESS_COLOR
            )
        else:
            emb = discord.Embed(
                title=f'Error',
                description=f"`{productid}` is not a valid product ID.",
                color=config.ERROR_COLOR
            )
            
        config.SET_EMBED_FOOTER(self, emb)
        await interaction.response.send_message(embed=emb, ephemeral=True)

    # ——————————————————————————————————————
    # LISTPRODUCTIDS COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="List all products and their IDs")
    @app_commands.checks.has_permissions(administrator=True)
    async def listproductids(self, interaction: discord.Interaction):
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
            embed.add_field(name="", value=f"There are no products in your marketplace.\n\nAdd a product using: `/addproduct [PROD_ID]`", inline=False)

        config.SET_EMBED_FOOTER(self, embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ——————————————————————————————————————
    # LISTARCHIVED COMMAND
    # ——————————————————————————————————————
    @app_commands.command(description="List all products archived in stripe")
    @app_commands.checks.has_permissions(administrator=True)
    async def listarchived(self, interaction: discord.Interaction):
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
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(description="Link to stripe dashboard")
    @app_commands.checks.has_permissions(administrator=True)
    async def stripedash(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"Stripe Dashboard", description="\n__**LIVE**__\n[Active Products](https://dashboard.stripe.com/products?active=true)\n\
                [Archived Products](https://dashboard.stripe.com/products?active=false)\n\n__**TEST**__\n[Active Products](https://dashboard.stripe.com/test/products?active=true)\n\
                [Archived Products](https://dashboard.stripe.com/test/products?active=false)",
            color=config.MAIN_COLOR
        )

        config.SET_EMBED_FOOTER(self, embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    
    @addproduct.error
    @removeproduct.error
    @listproductids.error
    @listarchived.error
    async def admin_error(self, interaction, error):
        if isinstance(error, MissingPermissions):
            emb = discord.Embed(title=f'Sorry {interaction.user}!', description="You do not have permissions to do that.",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Marketplace(bot))