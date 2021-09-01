import lib
from commands import Commands
from control import Control
from events import *

@lib.bot.event
async def on_ready():
    activity = discord.Game(name="c$help | Alpha v0.0.1", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("----------Bot is online!----------")

def setup(bot):
    for f in lib.files:
        try:  
            lib.bot.load_extension(f)
            print(f + ' was loaded!')
        except Exception as e:
            print(f + ' is not loaded! Error: ' + str(e))

setup(lib.bot)


lib.bot.run('Nzk5NzEzMTU2ODA0MTE2NTEx.YAHk6g.Ei9WOj4IIGjtXtMmpT6Cc4HMHHA')