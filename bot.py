import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

def main():
    command_prefix = "?"
    client = commands.Bot(command_prefix, intents=discord.Intents.all())
    client.remove_command('help')

    load_dotenv()

    @client.event
    async def on_ready():
        print("TEAZHI is connected.")

        await client.wait_until_ready()

        embed = discord.Embed(
            title = "Status",
            description = f"✅ {client.user.display_name} is online. ",
            color = discord.Color.green()
        )

        await client.get_channel(int("1092683599796514826")).send(embed=embed)

        # load cogs
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await client.load_extension(f"cogs.{file[:-3]}")

    client.run(os.getenv("TOKEN"))

if __name__ == '__main__':
    main()