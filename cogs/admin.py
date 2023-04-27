import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext.commands import Greedy, Context
from typing import Literal, Optional
import config

class Admin(commands.Cog, name="Admin"):
    """ | \
        List of all admin commands available"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(description="Reload all modules")
    @commands.is_owner()
    @has_permissions(administrator=True)
    async def reloadall(self, ctx, cog: str = None):
        if cog is not None:
            emb = discord.Embed(title=f'Error', description=f"Please use `{config.PREFIX}reload [MODULE]` to reload a specific module.",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
        else:
            for cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
            emb = discord.Embed(title=f'Success', description=f"All modules and commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
            await ctx.send(embed=emb)

    @commands.command(description="Reload a given module")
    @commands.is_owner()
    # @has_permissions(administrator=True)
    async def reload(self, ctx, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to reload. \n\n`Usage: {config.PREFIX}reload [MODULE]`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await ctx.send(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to reload.",
                                        color=config.ERROR_COLOR)
                await ctx.send(embed=emb) 
    
    @commands.command(description="Load in a given module")
    @commands.is_owner()
    @has_permissions(administrator=True)
    async def load(self, ctx, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to load. \n\n`Usage: {config.PREFIX}load [MODULE]`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.load_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await ctx.send(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to load.",
                                        color=config.ERROR_COLOR)
                await ctx.send(embed=emb) 

    @commands.command(description="Unload a given module")
    @commands.is_owner()
    @has_permissions(administrator=True)
    async def unload(self, ctx, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to unload. \n\n`Usage: {config.PREFIX}unload [MODULE]`",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.unload_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await ctx.send(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to unload.",
                                        color=config.ERROR_COLOR)
                await ctx.send(embed=emb)

    @commands.command(description="Sync command tree")
    @has_permissions(administrator=True)
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @reloadall.error
    @reload.error
    @load.error
    @unload.error
    async def admin_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            emb = discord.Embed(title=f'Sorry {ctx.message.author}!', description="You do not have permissions to do that.",
                                        color=config.ERROR_COLOR)
            await ctx.send(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))