TOKEN= ''

import discord
from discord.ext import commands
import requests
import random

import asyncio

from typing import List, Dict
rhyme_endpoint = "https://api.datamuse.com/words"
file_name = "3000_words_no_spaces.txt"
 
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

import tracemalloc
tracemalloc.start()

from collections import namedtuple

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

#command start testing
@bot.command()
async def start(ctx):

    players = []

    message = await ctx.send("Message")
    await message.add_reaction('✅')
    await asyncio.sleep(30)

    message = await ctx.fetch_message(message.id)

    for reaction in message.reactions:
        if reaction.emoji == '✅':
            async for user in reaction.users():
                if user != bot.user:
                    players.append(user.mention)

    if len(players) < 3:
        await ctx.send('Time is up, and not enough players')
    else:
        await ctx.send(players)




bot.run(TOKEN)
