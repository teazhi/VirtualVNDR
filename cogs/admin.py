import os
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from bot import command_prefix

class Admin(commands.Cog, name="Admin"):
    """ | \
        Admin Commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @has_permissions(administrator=True)
    async def reloadall(self, ctx: commands.Context, cog = None):
        if cog is not None:
            await ctx.send(f"Please use `{command_prefix}reload [MODULE]` to reload a specific module.")
        else:
            for cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
            await ctx.send(f"All modules and commands have been reloaded successfully. ✅")

    @commands.command()
    @has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context, cog = None):
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
    @has_permissions(administrator=True)
    async def load(self, ctx: commands.Context, cog = None):
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
    @has_permissions(administrator=True)
    async def unload(self, ctx: commands.Context, cog = None):
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

    @reloadall.error
    @reload.error
    @load.error
    @unload.error
    async def admin_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            emb = discord.Embed(title=f'ERROR', description="Sorry {}, you do not have permissions to do that!".format(ctx.message.author),
                                        color=discord.Color.red())
            await ctx.send(embed=emb, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))