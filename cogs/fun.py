import discord
from discord.ext import commands
import aiohttp

class Fun(commands.Cog):
    multiActionDict = {
        'bully': 'bullies',
        'cuddle': 'cuddles',
        'hug': 'hugs',
        'kiss': 'kisses',
        'pat': 'pats',
        'bonk': 'bonks',
        'yeet': 'yeets',
        'poke': 'pokes',
        'wave': 'waves to'
    }

    singleActionDict = {
        'cry': 'cries...',
        'smug': 'is feeling smug!',
        'blush': 'blushes...',
        'nom': 'eats something delicious!',
        'dance': 'breaks it down!',
        'cringe': 'cringes. Yikes.'
    }

    def __init__(self, client):
        self.client = client
        self.session = aiohttp.ClientSession()
    
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun cog is online.')

    # custom event to close the ClientSession
    @commands.Cog.listener()
    async def on_cog_unload_event(self):
        #print('Fun cog unloaded, closing ClientSession...')
        await self.session.close()

    # Commands
    # Single-User Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def waifu(self, ctx):
        async with self.session.get(f'https://api.waifu.pics/sfw/waifu') as req:
            res = await req.json()
            embed = discord.Embed(
                color=0xff0000
            )
            embed.set_image(url=res['url'])
            await ctx.send(embed=embed)

    @commands.command(aliases=[
        'smug', 'blush', 'nom', 'dance', 'cringe'
    ])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cry(self, ctx):
        com = ctx.invoked_with.lower()
        async with self.session.get(f'https://api.waifu.pics/sfw/{com}') as req:
            res = await req.json()
            embed = discord.Embed(
                description=f'{ctx.message.author.mention} {self.singleActionDict[com]}',
                color=0xff0000
            )
            embed.set_image(url=res['url'])
            await ctx.send(embed=embed)

    # Multi-User (Interaction) Commands
    @commands.command(aliases=[
        'cuddle', 'hug', 'kiss', 'pat', 'bonk', 'yeet', 'poke', 'wave'
    ])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def bully(self, ctx, *, member: discord.Member = None):
        # member: the user said action is applied to
        com = ctx.invoked_with.lower()
        invoker = ctx.message.author
        if not member or member.id == invoker.id:
            # if no member is specified, Kurisu will act as the invoker
            invoker = self.client.user
            member = ctx.message.author
        desc = f'{invoker.mention} {self.multiActionDict[com]} {member.mention}!'
        
        async with self.session.get(f'https://api.waifu.pics/sfw/{com}') as req:
            res = await req.json()
            embed = discord.Embed(
                description=desc,
                color=0xff0000
            )
            embed.set_image(url=res['url'])
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Fun(client))
