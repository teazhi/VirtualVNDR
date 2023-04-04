import os
from discord.ext import commands

class Admin(commands.Cog, name="Admin"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx: commands.Context, cog = None):
        command_prefix = "?"

        if cog is None:
            await ctx.send(f"Please provide a module to reload. \nUsage: {command_prefix}reload [MODULE]")
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
                await ctx.send(f"All [{cog}] commands have been reloaded successfully. ✅")
            else:
                await ctx.send(f"Please provide a valid module to reload.") 
    
    @commands.command()
    async def load(self, ctx: commands.Context, cog = None):
        command_prefix = "?"

        if cog is None:
            await ctx.send(f"Please provide a module to load. \nUsage: {command_prefix}load [MODULE]")
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.load_extension(f"cogs.{cog}")
                await ctx.send(f"All [{cog}] commands have been loaded successfully. ✅")
            else:
                await ctx.send(f"Please provide a valid module to load.") 

    @commands.command()
    async def unload(self, ctx: commands.Context, cog = None):
        command_prefix = "?"

        if cog is None:
            await ctx.send(f"Please provide a command category to unload. \nUsage: {command_prefix}unload [MODULE]")
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.unload_extension(f"cogs.{cog}")
                await ctx.send(f"All [{cog}] commands have been unloaded successfully. ✅")
            else:
                await ctx.send(f"Please provide a valid module to unload.") 

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))