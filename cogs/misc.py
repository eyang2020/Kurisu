import os
import discord
from discord.ext import commands
import random

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Misc cog is online.')

    # Commands
    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pfp(self, ctx, *, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        userAvatar = member.avatar_url
        await ctx.send(userAvatar)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def flip(self, ctx):
        x = random.randint(0, 1)
        res = 'Heads'
        if x == 0: res = 'Tails'
        await ctx.send(f'{ctx.message.author.mention}, the coin landed on **{res}**!')

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def roll(self, ctx):
        x = random.randint(1, 6)
        await ctx.send(f'{ctx.message.author.mention}, the die landed on **{x}**!')

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        await ctx.send('You can invite me to your server here! https://discord.com/oauth2/authorize?client_id=821852263894089788&permissions=347200&scope=bot')

def setup(client):
    client.add_cog(Misc(client))
