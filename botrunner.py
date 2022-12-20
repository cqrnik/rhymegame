TOKEN= 'MTA1NDc3NDE5NzkyODMzNzQzOQ.G3WugQ.r_Ph0t5SJJG7TC2Ek9ga2bQDB2X5nBBhLU9RZo'

import discord
import rhymegame
 
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
 
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
 
@client.event
async def on_message(message):
    print("message-->", message)
    if message.author == client.user:
        return
 
    if message.content.startswith('!start'): ##change this to exact match not starts with
        await message.channel.send('Hello!')
        await message.channel.send(rhymegame.full_game_iteration)
    
 
 
client.run(TOKEN)
