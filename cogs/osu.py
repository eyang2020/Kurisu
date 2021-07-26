import os
import discord
from discord.ext import commands
import pymongo
from osuapi import OsuApi, AHConnector
from math import floor
import random
from datetime import datetime

OSU_API_KEY = os.environ['OSU_API_KEY']
MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)
db = cluster.test
collection = db['Osu']

class Osu(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.osuClient = OsuApi(OSU_API_KEY, connector=AHConnector())

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Osu cog is online.')

    def cog_unload(self):
        #print('Closing osu connection...')
        self.osuClient.close()

    # Commands
    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def osu(self, ctx): 
        user = ctx.message.author
        doc = collection.find_one({'userId': user.id})
        if doc is None:
            await ctx.send(f'{user.mention}, please set your osu! profile using **k*setprofile [username]**.')
        else:
            osuUsername = doc['osuUsername']
            results = await self.osuClient.get_user(osuUsername)
            recent = await self.osuClient.get_user_recent(osuUsername, limit=1)
            username = results[0].username
            userId = results[0].user_id
            # format: url_to_img?random_code to force update rather than discord client-side cache
            profileImg = '{}?{}'.format(results[0].profile_image, random.randint(10000, 99999))
            #profileImg = results[0].profile_image
            #print(profileImg)
            cntRankSS = results[0].count_rank_ss
            cntRankS = results[0].count_rank_s
            cntRankA = results[0].count_rank_a
            accuracy = '{0:.2f}%'.format(results[0].accuracy)
            ppGlobalRank = '#{:,}'.format(results[0].pp_rank)
            ppCountryRank = '#{:,}'.format(results[0].pp_country_rank)
            ppRaw = round(results[0].pp_raw)
            level = floor(results[0].level)
            playcount = results[0].playcount
            joinDate = results[0].join_date
            dateStr = joinDate.strftime("%B %d, %Y")
            secondsPlayed = results[0].total_seconds_played
            minutesPlayed = secondsPlayed // 60
            hoursPlayed = minutesPlayed // 60
            #totalSecondsPlayed = int(results[0].total_seconds_played)
            #print(totalSecondsPlayed)
            embed = discord.Embed(description=f"Showing osu! profile for **[{username}](https://osu.ppy.sh/users/{userId})**", color=0xff0000)
            embed.add_field(name='<:SS:837015941429592073>', value=cntRankSS, inline=True)
            embed.add_field(name='<:S_:837015941912461313>', value=cntRankS, inline=True)
            embed.add_field(name='<:A_:837015454119755818>', value=cntRankA, inline=True)
            embed.add_field(name='pp', value=ppRaw, inline=True)
            embed.add_field(name='global rank', value=ppGlobalRank, inline=True)
            embed.add_field(name='country rank', value=ppCountryRank, inline=True)
            embed.add_field(name='accuracy', value=accuracy, inline=True)
            embed.add_field(name='level', value=level, inline=True)
            embed.add_field(name='playcount', value=playcount, inline=True)
            embed.add_field(name='date joined', value=dateStr, inline=True)
            if hoursPlayed > 0:
                embed.add_field(name='playtime', value='{} hours'.format(hoursPlayed), inline=True)
            else:
                embed.add_field(name='playtime', value='{} minutes'.format(minutesPlayed), inline=True)
            if len(recent) > 0:
                beatmapStr = ''
                recentBeatmap = recent[0]
                recentBeatmapId = recentBeatmap.beatmap_id
                beatmap = await self.osuClient.get_beatmaps(beatmap_id=recentBeatmapId)
                title = beatmap[0].title
                creator = beatmap[0].creator
                beatmapStr += '[{} by {}](http://osu.ppy.sh/beatmaps/{})\n'.format(title, creator, recentBeatmapId)
                embed.add_field(name='recently played', value=beatmapStr, inline=False)
                
            embed.set_thumbnail(url=profileImg)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

    @commands.command(aliases=['sp'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def setprofile(self, ctx, username=None):
        user = ctx.message.author
        if username is None:
            await ctx.send(f'{user.mention}, please set your osu! profile using **k*setprofile [username]**.')
        elif len(username) > 15:
            # osu! usernames have a 15 character limit
            await ctx.send(f'{user.mention}, I could not find a profile with that username. Check that your username is correct and that your profile is public.')
        else:
            # check if this username leads to a valid osu! profile
            results = await self.osuClient.get_user(username)
            if len(results) == 0:
                await ctx.send(f'{user.mention}, I could not find the user **{username}**. Check that your username is correct and that your profile is public.')
            else:
                # get the correct capitalization
                osuUsername = results[0].username
                collection.update_one({'userId': user.id}, {"$set": {'osuUsername': osuUsername}}, upsert=True)
                await ctx.send(f'{user.mention}, your osu! username has been set to **{osuUsername}**.')

def setup(client):
    client.add_cog(Osu(client))
