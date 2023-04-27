import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import config

def main():
    client = commands.Bot(
        config.PREFIX,
        owner_id = 853288012851314729,
        intents=discord.Intents.all(), 
        status=discord.Status.dnd, 
        activity=discord.Activity(type=discord.ActivityType.watching, name='teazhi work on marketplace')
    )
    client.remove_command('help')

    load_dotenv()

    @client.event
    async def on_ready():
        await client.wait_until_ready()

        print("━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"{client.user} is connected.")
        print("━━━━━━━━━━━━━━━━━━━━━━━")

        # load cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    await client.load_extension(f"cogs.{file[:-3]}")
                    print(f"{file[:-3]} loaded.")
                except commands.ExtensionAlreadyLoaded:
                    print(f"{file[:-3]} is already loaded.")
        print("━━━━━━━━━━━━━━━━━━━━━━━")

    client.run(os.getenv("TOKEN"))

if __name__ == '__main__':
    main()