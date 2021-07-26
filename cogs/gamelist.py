import os
import discord
from discord.ext import commands
import pymongo
import random

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)
db = cluster.test
collection = db['Gamelist']

class Gamelist(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Gamelist cog is online.')

    # Commands
    @commands.command(aliases=['gl'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def gamelist(self, ctx):
        userId = ctx.message.author.id
        await self.initGameList(userId)
        doc = collection.find_one({'userId': userId})
        gameList = doc['gameList']
        gameListStr = ''
        embed=discord.Embed(description=f'**Showing gamelist for {ctx.author.mention}**', color=0xff0000)
        for game in gameList:
            gameListStr += game + '\n'
        embed.add_field(name='\u200b', value=gameListStr+'\u200b', inline=False) # value cannot = '', so we append the blank char.
        embed.set_footer(text="Showing page 1/1")
        await ctx.send(embed=embed)

    @commands.command(aliases=['ag'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def addgame(self, ctx, *gameTitle):
        gameTitle =  ' '.join(gameTitle)
        length = len(gameTitle)
        user = ctx.message.author
        if length == 0:
            await ctx.send(f'{user.mention}, add a game using **k*addgame** [**title**].')
        elif length > 30:
            await ctx.send(f'{user.mention}, the game title is too long, please enter a shortcut.')
        else:
            userId = ctx.message.author.id
            await self.initGameList(userId)
            await ctx.send(f'{user.mention}, **{gameTitle}** has been added to your gamelist.')
            collection.update_one({'userId': userId}, {'$addToSet': {'gameList': gameTitle.lower()}})

    @commands.command(aliases=['rg'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def removegame(self, ctx, *gameTitle):
        gameTitle =  ' '.join(gameTitle)
        length = len(gameTitle)
        user = ctx.message.author
        if length == 0:
            await ctx.send(f'{user.mention}, remove a game using **k*removegame** [**title**].')
        elif length > 30:
            await ctx.send(f'{user.mention}, the game title is too long, please enter a shortcut.')
        else:
            userId = user.id
            await self.initGameList(userId)
            await ctx.send(f'{user.mention}, **{gameTitle}** has been removed from your gamelist.')
            collection.update_one({'userId': userId}, {'$pull': {'gameList': gameTitle.lower()}})

    @commands.command(aliases=['pg'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pickgame(self, ctx):
        user = ctx.message.author
        userId = user.id
        await self.initGameList(userId)
        doc = collection.find_one({'userId': userId})
        gameList = doc['gameList']
        if not gameList:
            await ctx.send(f'{user.mention}, your gamelist is empty. Add a game using **k*addgame** [**title**].')
        else:
            await ctx.send(f'{user.mention}, I think you should play **{random.choice(gameList)}**!')

    # Other methods
    async def initGameList(self, userId):
        doc = collection.find_one({'userId': userId})
        if doc == None:
            newEntry = ({'userId': userId, 'gameList': []})
            collection.insert_one(newEntry)

def setup(client):
    client.add_cog(Gamelist(client))