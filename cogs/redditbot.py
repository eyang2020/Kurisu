import os
import discord
from discord.ext import commands
import asyncpraw
import random

REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USERNAME = os.environ['REDDIT_USERNAME']
REDDIT_PASSWORD = os.environ['REDDIT_PASSWORD']

class RedditBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reddit = asyncpraw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD, 
            user_agent='pythonpraw'
        )

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('RedditBot cog is online.')

    # custom event to close the asyncpraw session
    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        #print('RedditBot cog unloaded, closing asyncpraw session...')
        await self.reddit.close()

    # Commands
    '''
    # This command allows a user to lookup a random post on any subreddit.
    # Currently disabled.
    @commands.command(aliases=['r'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reddit(self, ctx, inputSubreddit='animemes'):
        # check if inputSubreddit is a valid subreddit
        if inputSubreddit.startswith(('/r/', 'r/')):
            inputSubreddit = inputSubreddit.split('r/')[-1]
        try:
            subreddit = await reddit.subreddit(inputSubreddit, fetch=True)
        except:
            await ctx.send(f'The subreddit **{inputSubreddit}** does not exist.')
            return
        allSubmissions = []

        async for submission in subreddit.hot(limit=50):
            allSubmissions.append(submission)
        randomSubmission = random.choice(allSubmissions)
        url = randomSubmission.url
        fileFormat = url.split('.')[-1]
        cnt = 0
        foundImage = True
        while fileFormat not in ['jpeg', 'jpg', 'png', 'gif']:
            # none of these submissions are images or gifs
            if cnt >= 50:
                foundImage = False
                break
            randomSubmission = random.choice(allSubmissions)
            url = randomSubmission.url
            fileFormat = url.split('.')[-1].lower()
            cnt += 1

        if not foundImage:
            await ctx.send('There were no image/gif posts, maybe try another subreddit...')
        else:
            name = randomSubmission.title
            link = 'https://www.reddit.com' + randomSubmission.permalink
            upvoteCnt = randomSubmission.score
            embed = discord.Embed(title=name, url=link, color=0xff0000)
            embed.set_image(url=url)
            embed.set_footer(text=f'⬆️ {upvoteCnt} | r/{subreddit.display_name}')
            await ctx.send(embed=embed)
    '''

    @commands.command(aliases=['am'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def animeme(self, ctx):
        subredditList = ['animemes', 'goodanimemes']
        subreddit = await self.reddit.subreddit(random.choice(subredditList), fetch=True)
        allSubmissions = []

        async for submission in subreddit.hot(limit=50):
            allSubmissions.append(submission)
        randomSubmission = random.choice(allSubmissions)
        url = randomSubmission.url
        fileFormat = url.split('.')[-1]
        cnt = 0
        foundImage = True
        while fileFormat not in ['jpeg', 'jpg', 'png', 'gif']:
            # none of these submissions are images or gifs
            if cnt >= 50:
                foundImage = False
                break
            randomSubmission = random.choice(allSubmissions)
            url = randomSubmission.url
            fileFormat = url.split('.')[-1].lower()
            cnt += 1

        if not foundImage:
            await ctx.send('There were no valid posts.')
        else:
            name = randomSubmission.title
            link = 'https://www.reddit.com' + randomSubmission.permalink
            upvoteCnt = randomSubmission.score
            embed = discord.Embed(title=name, url=link, color=0xff0000)
            embed.set_image(url=url)
            embed.set_footer(text=f'⬆️ {upvoteCnt} | r/{subreddit.display_name}')
            await ctx.send(embed=embed)
    
def setup(client):
    client.add_cog(RedditBot(client))
