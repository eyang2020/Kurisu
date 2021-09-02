import os
import keep_alive
import discord
from discord.ext import commands
import asyncio
from datetime import datetime

TOKEN = os.environ['DISCORD_TOKEN']
client = commands.Bot(command_prefix=['k*', 'K*'], help_command=None, case_insensitive=True)
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
COG_FOLDER = os.path.join(THIS_FOLDER, 'cogs')

# cdDict is a cache that stores a list of the user id's of users who are on cd for a command
cdDict = {
    'help': [],

    'anime': [],
    #'manga': [],

    'animeme': [],

    'blackjack': [],

    'daily': [],
    'balance': [],

    '_02': [],
    'chika': [],
    'nam': [],
    'ayaya': [],
    'pog': [],
    'uwu': [],
    'sus': [],
    'eject': [],

    'pfp': [],
    'flip': [],
    'roll': [],
    'invite': [],
    'support': [],

    'waifu': [],
    'cry': [],
    'bully': [],

    'setprofile': [],
    'osu': [],
    
    'serverdropadd': [],
    'serverdropremove': [],
    'stats': [],
    'calcmode': []
}

# Commands
@client.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

@client.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension=None):
    embed=discord.Embed(
        title='Cog Reload Status:',
        color=0xff0000
    )
    status = ''
    if extension is None:
        # reload all cogs
        # cog_unload_event is a custom event to signal a ClientSession must be closed in that cog
        client.dispatch('cog_unload_event')
        for fileName in os.listdir(COG_FOLDER):
            if fileName.endswith('.py'):
                extension = fileName[:-3]
                try:
                    client.unload_extension(f'cogs.{extension}')
                    client.load_extension(f'cogs.{extension}')
                    status += '✅`{}`\n'.format(extension)
                except:
                    status += '❌`{}`\n'.format(extension)
    else:
        # reload the specified cog
        if extension == 'redditbot' or extension == 'fun':
            client.dispatch('cog_unload_event')
        try:
            client.unload_extension(f'cogs.{extension}')
            client.load_extension(f'cogs.{extension}')
            status = '✅`{}`'.format(extension)
        except:
            status = '❌`{}`'.format(extension)
    # send report
    embed.add_field(name='\u2800', value=status, inline=False)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

@client.command(hidden=True)
@commands.is_owner()
async def count(ctx):
    serverCnt = len(client.guilds)
    memberCnt = 0
    for guild in client.guilds:
        memberCnt += guild.member_count - 1
    
    await ctx.send(f'Watching over {memberCnt} users in {serverCnt} servers.')

    embed=discord.Embed(
        title='Bot Statistics',
        description=f'Chilling with {memberCnt} users\nWatching {serverCnt} servers',
        color=0xff0000
    )

    serverStr = ''

    for server in client.guilds:
        serverStr += f'{server}\n'

    embed.add_field(name='Server List', value=serverStr, inline=False)

    await ctx.send(embed=embed)

# begin by loading all cogs
for fileName in os.listdir(COG_FOLDER):
    if fileName.endswith('.py'):
        client.load_extension(f'cogs.{fileName[:-3]}')

# Events
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='k*help'), status=discord.Status.online)
    print("KurisuBot is online.")

# Error Handling (Event)
@client.event
async def on_command_error(ctx, error):
    #print(f'Error: {error}')
    # Cooldown Errors
    if isinstance(error, commands.CommandOnCooldown):
        #print(ctx.command)
        user = ctx.message.author
        userId = user.id
        com = str(ctx.command).lower()
        if userId not in cdDict[com]:
            cdDict[com].append(userId)
            secondsLeft = round(error.retry_after)
            if com != 'daily':
                # the cdDict for daily is for the on cooldown error message
                await ctx.send(f'{user.mention}, this command is on a `{secondsLeft} second` cooldown')
            await asyncio.sleep(secondsLeft)
            cdDict[com].remove(userId)

keep_alive.keep_alive()
client.run(TOKEN)
