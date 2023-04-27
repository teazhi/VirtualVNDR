import discord
import os
import datetime

PREFIX = "?"
BOT_VERSION = "v1.0"
OWNER_ID = "853288012851314729"
OWNER_NAME = "teazhi#7831"
MY_GUILD = discord.Object(id = 1092628564324659290)

MAIN_COLOR = discord.Color.from_rgb(210, 43, 43)
ERROR_COLOR = discord.Color.red()
SUCCESS_COLOR = discord.Color.green()

LOGO_URL = "https://media.giphy.com/media/S2S0ZDytY6yDm/giphy.gif"

MPFILEPATH = os.path.join(os.path.dirname(__file__), 'marketplaceItems.json')

def SET_EMBED_FOOTER(self, emb):
    emb.timestamp = datetime.datetime.now()
    emb.set_footer(text=f'{self.bot.user.display_name} {BOT_VERSION} | by {OWNER_NAME}', icon_url=LOGO_URL)
