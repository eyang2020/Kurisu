import os
from discord.ext import commands
import pymongo
import random
from datetime import datetime

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)

db = cluster.test
collection = db['Economy']
cache = {} # in form of userId : datetimeOfLastSuccessfulInvoke

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Economy cog is online.')

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def daily(self, ctx): 
        user = ctx.message.author
        userId = user.id
        now = datetime.now()
        lastInvoke = None
        canInvoke = True
        if userId not in cache:
            #print('user not in cache')
            # check db
            await self.openAccount(userId) # need to make sure user has an account first
            doc = collection.find_one({'userId': userId})
            lastInvoke = doc['lastInvoke']
            if lastInvoke:
                # add this user into the cache
                cache[userId] = lastInvoke
                # convert lastInvoke from string to a datetime object
                lastInvoke = datetime.strptime(lastInvoke, '%m/%d/%Y, %H:%M:%S')
        else:
            #print('user in cache')
            # check cache
            lastInvoke = datetime.strptime(cache[userId], '%m/%d/%Y, %H:%M:%S')
        # calculate how many seconds have passed since last successful invocation
        if lastInvoke:
            secondsPassed = (now - lastInvoke).total_seconds()
            if secondsPassed <= 86400:
                # report on cooldown
                canInvoke = False
                secondsLeft = 86400 - secondsPassed
                minutesLeft = secondsLeft // 60
                hoursLeft = int(minutesLeft // 60)
                minutesLeft = int(minutesLeft % 60)
                if hoursLeft > 0:
                    await ctx.send(f'{user.mention}, you can claim your daily upa in `{hoursLeft} hours and {minutesLeft} minutes`.')
                else:
                    await ctx.send(f'{user.mention}, you can claim your daily upa in `{minutesLeft} minutes`.')
        if canInvoke:
            # successfully invoke the daily command
            nowStr = now.strftime('%m/%d/%Y, %H:%M:%S')
            earnings = random.randint(500, 1000)
            await ctx.send(f'{user.mention}, you received **{earnings}** upa!')
            # metal upa (5% chance)
            if random.random() < 0.05:
                earnings += 500
                await ctx.send(f'{user.mention}, a **metal upa** rolled out of the machine, giving you an additional **500** upa!')
            # calculate user's new upa balance
            doc = collection.find_one({'userId': userId})
            newUpaCnt = doc['upa'] + earnings
            # update cache
            cache[userId] = nowStr
            # update db
            collection.update_one({'userId': userId}, {'$set': {'upa': newUpaCnt, 'lastInvoke': nowStr}})

    @commands.command(aliases=['b'])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def balance(self, ctx):
        user = ctx.message.author
        await self.openAccount(user.id)
        doc = collection.find_one({'userId': user.id})
        # output user's upa balance
        upaCnt = doc['upa']
        await ctx.send(f'{user.mention}, you currently have **{upaCnt}** upa.')

    # Other methods
    async def openAccount(self, userId):
        doc = collection.find_one({'userId': userId})
        if doc == None:
            newEntry = ({'userId': userId, 'upa': 0, 'lastInvoke': None})
            collection.insert_one(newEntry)

def setup(client):
    client.add_cog(Economy(client))
