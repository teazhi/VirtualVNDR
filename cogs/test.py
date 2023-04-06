import discord
from discord.ui import Select, View
from discord.ext import commands

class Test(commands.Cog, name="Test"):
    """ | Command for testing purposes"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Test dropdown menu")
    async def testdropdown(self, ctx: commands.Context):
        select = Select(options=[
            discord.SelectOption(label="Day", emoji="☀️", description="Select day option"),
            discord.SelectOption(label="Night", emoji="🌜", description="Select night option"),
        ])

        async def doSmthCallback(interation):
            await interation.response.send_message(f"You chose: {select.values}")
        
        select.callback = doSmthCallback

        view = View()
        view.add_item(select)

        await ctx.send("Choose an option", view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))