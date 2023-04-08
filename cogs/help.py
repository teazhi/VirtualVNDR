import discord
from discord.ext import commands
from discord.errors import Forbidden
import config
import datetime

async def send_embed(self, ctx, embed):
    try:
        config.SET_EMBED_FOOTER(self,embed)
        await ctx.send(embed=embed, ephemeral=True)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile: ", embed=embed)


class Help(commands.Cog):
    """ | Display help information about the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.bot_has_permissions(add_reactions=True,embed_links=True)
    async def help(self, ctx, *input):
        """Shows all modules of that bot"""
        # checks if cog parameter was given
        # if not: sending all modules and commands not associated with a cog
        if not input:
            # checks if owner is on this server - used to 'tag' owner
            try:
                config.OWNER_ID = ctx.guild.get_member(config.OWNER_ID).mention

            except AttributeError as e:
                config.OWNER_ID = config.OWNER_ID

            # starting to build embed
            emb = discord.Embed(
                title=f'{ctx.guild.name} - Server', color=discord.Color.from_rgb(210, 43, 43),
                description=f'Commands in the server start with `{config.PREFIX}`\n\
                            Use `{config.PREFIX}help <module>` to find commands under that module '
                            f':smiley:\n'
            )

            # iterating trough cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                if cog == "Admin":
                    continue
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            # adding 'list' of cogs to embed
            emb.add_field(name='Modules', value=cogs_desc, inline=False)

            # integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

            # setting information about author
            emb.add_field(name="About", value=f"Meet TEAZHI, the multi-purpose ecommerce Discord bot revolutionizing online shopping. Shop directly\
                                                in the server with automated services and real-time customer support, making online shopping easier\
                                                and more efficient than ever before.")
            
            emb.add_field(name="", value="", inline=False)
            
            # REMOVE GITHUB LINK WHEN SHOWING THIS TO THE PUBLIC
            emb.add_field(name="", value="**[[GitHub](https://github.com/teazhi/TEAZHI_Bot)]** ✦ **[[Website](https://www.teazhitz.com)]**", inline=False)
            # emb.add_field(name="", value="", inline=True)

        # block called when one cog-name is given
        # trying to find matching cog and it's commands
        elif len(input) == 1:

            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == input[0].lower():
                    if cog.lower() == "admin":
                        if not ctx.author.guild_permissions.administrator:
                            emb = discord.Embed(title=f'Error', description="Sorry {}, you do not have permissions to do that!".format(ctx.message.author),
                                        color=config.ERROR_COLOR)
                            break

                    # making title - getting description from doc-string below class
                    emb = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__[2:],
                                        color=discord.Color.from_rgb(210, 43, 43))

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            if command.usage is None:
                                command.usage = ""
                            emb.add_field(name=f"`{config.PREFIX}{command.name}{command.usage}`", value=f" - {command.description}", inline=False)
                    # found cog - breaking loop
                    break

            # if input not found
            # yes, for-loops have an else statement, it's called when no 'break' was issued
            else:
                emb = discord.Embed(title="Invalid Module",
                                    description=f"I've never heard of a module called `{input[0]}` before :thinking:",
                                    color=discord.Color.orange())

        # too many cogs requested - only one at a time allowed
        elif len(input) > 1:
            emb = discord.Embed(title="Invalid number of arguments",
                                description="Please request only one module at a time :sweat_smile:",
                                color=discord.Color.orange())

        else:
            emb = discord.Embed(title="It's a magical place.",
                                description="I don't know how you got here. But I didn't see this coming at all.\n"
                                            "Would you please be so kind to report that issue to me on discord?\n"
                                            "Discord: teazhi#7831\n"
                                            "Thank you! ~teazhi",
                                color=config.ERROR_COLOR)

        # sending reply embed using our own function defined above
        await send_embed(self, ctx, emb)

async def setup(bot):
    await bot.add_cog(Help(bot))