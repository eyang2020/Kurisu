import os
import discord
from discord.ext import commands
import pymongo
from datetime import date

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)
db = cluster.test
collection = db['Stats']

class Stats(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Stats cog is online.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 646937666251915264: # message is from Karuta Bot
            serverId = message.guild.id
            await self.initStats(serverId)
            doc = collection.find_one({'serverId': serverId})
            if 'is dropping' in message.content: # drop count from all users
                newDropCnt = doc['dropCnt'] + 1
                collection.update_one({'serverId': serverId}, {'$set': {'dropCnt': newDropCnt}})
            elif 'currently active!' in message.content: # drop count due to server activity
                newDropCnt = doc['serverDropCnt'] + 1
                collection.update_one({'serverId': serverId}, {'$set': {'serverDropCnt': newDropCnt}})

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '⭐' and reaction.count == 1:
            serverId = reaction.message.guild.id
            await self.initStats(serverId)
            doc = collection.find_one({'serverId': serverId})
            newDropCnt = doc['pogDropCnt'] + 1
            collection.update_one({'serverId': serverId}, {'$set': {'pogDropCnt': newDropCnt}})

    # Commands
    @commands.command(aliases=['s'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx):
        serverName = ctx.message.guild.name
        serverId = ctx.message.guild.id
        statStr = ''
        await self.initStats(serverId)
        doc = collection.find_one({'serverId': serverId})
        dropCnt = doc['dropCnt']
        serverDropCnt = doc['serverDropCnt']
        pogDropCnt = doc['pogDropCnt']
        joinDate = doc['joinDate']
        # create the embed
        embed=discord.Embed(description=f'Showing statistics for **{serverName}**', color=0xff0000)
        statStr += f':drop_of_blood: User drops: **{dropCnt}**' + '\n'
        statStr += f':robot: Server drops: **{serverDropCnt}**' + '\n'
        statStr += f':star: Pog drops: **{pogDropCnt}**' + '\n'
        embed.add_field(name='\u200b', value=statStr+'\u200b', inline=False) # value cannot = '', so we append the blank char.
        embed.set_footer(text=f'Since {joinDate}')
        await ctx.send(embed=embed)

    # Other methods
    async def initStats(self, serverId):
        doc = collection.find_one({'serverId': serverId})
        if doc == None:
            joinDate = '{today:%B} {today.day}, {today.year}'.format(today = date.today())
            newEntry = ({'serverId': serverId, 'dropCnt': 0, 'serverDropCnt': 0, 'pogDropCnt': 0, 'joinDate': joinDate})
            collection.insert_one(newEntry)

def setup(client):
    client.add_cog(Stats(client))
