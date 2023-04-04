from discord.ext import commands

class Ping(commands.Cog, name="Ping"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Ping command")
    async def ping(self, ctx: commands.Context):
        await ctx.send("Pong!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))