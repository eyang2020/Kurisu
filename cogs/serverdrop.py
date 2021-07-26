import os
from discord.ext import commands
import pymongo

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)
db = cluster.test
collection = db['ServerDrop']

# 5/1/2021: ServerDrop now works by-server, rather than by-user.

class ServerDrop(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('ServerDrop cog is online.')

    @commands.Cog.listener()
    async def on_message(self, message):
        # check if message author is Karuta and server drop
        if message.author.id == 646937666251915264 and 'currently active!' in message.content:
            serverId = message.guild.id
            channel = message.channel
            # list of user ID's to be mentioned upon a server drop.
            # user ID's stored in the form of: <@...> for mention purposes
            try:
                doc = collection.find_one({'serverId': serverId})
                userIdList = doc['userId']
                await channel.send(f'Server drop! {" ".join(userIdList)}')
            except:
                pass

    # Commands
    @commands.command(aliases=['sda'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serverdropadd(self, ctx):
        serverId = ctx.message.guild.id
        # userId stored in a unique way so mention is created upon sending it in as a message
        userId = '<@' + str(ctx.message.author.id) + '>'
        await ctx.send(f'{userId}, you will now be pinged when there is a server drop.')
        # add this user mention to the array under the current server id
        collection.update_one({'serverId': serverId}, {'$addToSet': {'userId': userId}}, upsert = True)

    @commands.command(aliases=['sdr'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serverdropremove(self, ctx):
        serverId = ctx.message.guild.id
        userId = '<@' + str(ctx.message.author.id) + '>'
        await ctx.send(f'{userId}, you will no longer be pinged when there is a server drop.')
        # remove this user mention from array under the current server id
        collection.update_one({'serverId': serverId}, {'$pull': {'userId': userId}})

def setup(client):
    client.add_cog(ServerDrop(client))    
