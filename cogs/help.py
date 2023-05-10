import discord
from discord.ext import commands
from discord.errors import Forbidden
import config
import datetime
from discord.ext.commands import has_permissions, MissingPermissions
from discord import app_commands

class Help(commands.Cog):
    """ | Display help information about the bot"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Display help information about the bot")
    async def help(self, interaction: discord.Interaction):
        """Shows all modules of that bot"""

        # checks if owner is on this server - used to 'tag' owner
        try:
            config.OWNER_ID = interaction.guild.get_member(config.OWNER_ID).mention

        except AttributeError as e:
            config.OWNER_ID = config.OWNER_ID

        # starting to build embed
        emb = discord.Embed(
            title=f'Server: {interaction.guild.name}', color=discord.Color.from_rgb(210, 43, 43),
            description=f"Admin commands in the server start with `{config.PREFIX}`",
        )
        emb.add_field(name="__                                        __", value="", inline=False)

        # iterating trough cogs, gathering descriptions
        allcmds = '>>> '
        for cog in self.bot.cogs:
            if cog == "Admin" or cog == "Help" or cog == "Test":
                continue
            for command in self.bot.get_cog(cog).get_app_commands():
                allcmds += f'**/{command.name}**\n{command.description}\n\n'

            emb.add_field(name=f'{cog}', value=allcmds, inline=False)
            allcmds = '>>> '

        # integrating trough uncategorized commands
        commands_desc = ''
        for command in self.bot.walk_commands():
            # if cog not in a cog
            # listing command if cog name is None and command isn't hidden
            if not command.cog_name and not command.hidden:
                commands_desc += f'>>> **{command.name}** - {command.help}\n'

        # adding those commands to embed
        if commands_desc:
            emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

        emb.add_field(name="__                                        __", value="", inline=False)

        # setting information about author
        emb.add_field(name="About", value=f"Meet VirtualVNDR, the multi-purpose ecommerce bot revolutionizing marketplace experience on Discord. Shop directly\
                                            in the server with automated services and real-time customer support, making online shopping easier\
                                            and more efficient than ever before.")
        
        emb.add_field(name="", value="", inline=False)
        
        # REMOVE GITHUB LINK WHEN SHOWING THIS TO THE PUBLIC
        emb.add_field(name="", value="**[[Invite Me](https://discord.com/api/oauth2/authorize?client_id=1092661101163991091&permissions=8&scope=bot)]** ✦ **[[Discord](https://discord.gg/PDNgS9WHsF)]** ✦ **[[GitHub](https://github.com/teazhi/VirtualVNDR)]** ✦ **[[Website](https://www.teazhitz.com)]**", inline=False)
        emb.add_field(name="__                                        __", value="", inline=False)

        # sending reply embed using our own function defined above
        try:
            config.SET_EMBED_FOOTER(self,emb)
            await interaction.response.send_message(embed=emb, ephemeral=False)
        except Forbidden:
            try:
                await interaction.response.send_message("Hey, seems like I can't send embeds. Please check my permissions :)")
            except Forbidden:
                await interaction.user.send(
                    f"Hey, seems like I can't send any message in {interaction.channel.name} on {interaction.guild.name}\n"
                    f"May you inform the server team about this issue? :slight_smile: ", embed=emb)


    @app_commands.command(description="Begin the setup for your servers marketplace")
    # @has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Let us begin the setup for your servers marketplace.",
            description=f"\nStart by providing a general command prefix:",
            color=config.MAIN_COLOR
        )

        await interaction.response.send_message(embed=emb)


async def setup(bot):
    await bot.add_cog(Help(bot))