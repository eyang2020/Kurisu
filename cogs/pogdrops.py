import discord
from discord.ext import commands
import datetime

class PogDrops(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('PogDrops cog is online.')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        # the user parameter is the person who adds the reaction
        if reaction.emoji == '⭐' and reaction.count == 1: # prevent the embed being added multiple times
            # check that the message is from Karuta
            message = reaction.message
            if message.author.id == 646937666251915264:
                content = message.content
                mentionList = message.mentions
                dropper = message.author # initially set to KarutaBot (assume server drop)
                # searches current guild (server) for first text-channel named 'pog-drops'
                channel = discord.utils.find(lambda c: c.name == 'pog-drops', message.guild.text_channels)
                if channel is None:
                    # did not find a text-channel named pog-drops in current guild
                    channel = message.channel
                    await channel.send(f'{user.mention}, please create a text-channel named **"pog-drops"** for me to record your pog drops!')
                    return
                # check for any mentions in this message. if there are none, it was a server drop.
                # otherwise this drop is from a user.
                if mentionList:
                    dropper = mentionList[0] # user who invoked the drop
                    # change content to remove the expiration, if any
                    # should be in the format {dropper} is dropping n cards!
                    content = content.split('!')[0] + '!'
                else:
                    # server drop
                    content = 'I\'m dropping 3 cards since this server is currently active!'
                try:
                    # create the embed
                    embed = discord.Embed(description=content, color=0xff0000)
                    embed.set_author(name=dropper.name, icon_url=dropper.avatar_url)
                    embed.set_image(url=message.attachments[0].url)
                    embed.add_field(name='\u2800', value=f'[**Jump to drop!**]({message.jump_url})', inline=False)
                    embed.set_footer(text = f' ⭐ {reaction.count} | # {message.channel.name}')
                    embed.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embed)
                except:
                    pass

def setup(client):
    client.add_cog(PogDrops(client))
