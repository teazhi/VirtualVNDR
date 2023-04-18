import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext.commands import has_permissions, MissingPermissions
import config

class Admin(commands.Cog, name="Admin"):
    """ | \
        List of all admin commands available"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Reload all modules")
    @has_permissions(administrator=True)
    async def reloadall(self, interaction: discord.Interaction, cog: str = None):
        if cog is not None:
            emb = discord.Embed(title=f'Error', description=f"Please use `{config.PREFIX}reload [MODULE]` to reload a specific module.",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)
        else:
            for cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
            emb = discord.Embed(title=f'Success', description=f"All modules and commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
            await interaction.response.send_message(embed=emb)

    @app_commands.command(description="Reload a given module")
    @has_permissions(administrator=True)
    async def reload(self, interaction: discord.Interaction, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to reload. \n\n`Usage: {config.PREFIX}reload [MODULE]`",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.reload_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await interaction.response.send_message(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to reload.",
                                        color=config.ERROR_COLOR)
                await interaction.response.send_message(embed=emb) 
    
    @app_commands.command(description="Load in a given module")
    @has_permissions(administrator=True)
    async def load(self, interaction: discord.Interaction, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to load. \n\n`Usage: {config.PREFIX}load [MODULE]`",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.load_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await interaction.response.send_message(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to load.",
                                        color=config.ERROR_COLOR)
                await interaction.response.send_message(embed=emb) 

    @app_commands.command(description="Unload a given module")
    @has_permissions(administrator=True)
    async def unload(self, interaction: discord.Interaction, cog: str = None):
        if cog is None:
            emb = discord.Embed(title=f'Error', description=f"Please provide a module to unload. \n\n`Usage: {config.PREFIX}unload [MODULE]`",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)
        else:
            cog = str(cog).capitalize()
            if cog in self.bot.cogs:
                cog = cog.lower()
                await self.bot.unload_extension(f"cogs.{cog}")
                emb = discord.Embed(title=f'Success', description=f"All [{cog}] commands have been reloaded successfully. ✅",
                                        color=config.SUCCESS_COLOR)
                await interaction.response.send_message(embed=emb)
            else:
                emb = discord.Embed(title=f'Error', description=f"Please provide a valid module to unload.",
                                        color=config.ERROR_COLOR)
                await interaction.response.send_message(embed=emb) 

    @reloadall.error
    @reload.error
    @load.error
    @unload.error
    async def admin_error(self, interaction: discord.Interaction, error):
        if isinstance(error, MissingPermissions):
            emb = discord.Embed(title=f'Sorry {interaction.user}!', description="You do not have permissions to do that.",
                                        color=config.ERROR_COLOR)
            await interaction.response.send_message(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))