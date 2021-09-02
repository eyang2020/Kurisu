import discord
from discord.ext import commands

class Help(commands.Cog):
    asciiArtDict = {
        '02': 'Zero Two from DARLING in the FRANXX.',
        'chika': 'Chika from Kaguya-sama: Love Is War.',
        'nam': '"NaM or Die".',
        'ayaya': 'AYAYA.',
        'pog': 'Pog.',
        'uwu': 'uwu.',
        'sus': 'an imposter. Very sus!',
    }
    animeDict = {
        'cry': 'crying.',
        'smug': 'being smug',
        'blush': 'blushing.',
        'nom': 'eating.',
        'dance': 'dancing.',
        'cringe': 'cringing.',
        'bully': 'bullying',
        'cuddle': 'cuddling',
        'hug': 'hugging',
        'kiss': 'kissing',
        'pat': 'patting',
        'bonk': 'bonking',
        'yeet': 'yeeting',
        'poke': 'poking',
        'wave': 'waving to'
    }

    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Help cog is online.')

    # Commands
    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def help(self, ctx, com=None):
        # com represents a particular command k*[com]
        if com:
            com = com.lower()
            descriptionStr = ''
            embed=discord.Embed(
                title=f'Showing info for command: `{com}`',
                color=0xff0000
            )
            # more information has been requested for a custom command
            if com == 'animeme':
                descriptionStr = '''
                Sends a random anime meme from Reddit posted within the last week.
                Subreddits include r/animeme and r/goodanimemes.
                '''
                embed.add_field(name='Shortcuts', value='`am`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'anime':
                descriptionStr = '''
                Get information about a specific anime.
                Information is provided by the MyAnimeList and AniList API.
                '''
                embed.add_field(name='Usage', value='`k*anime` `anime`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
                """elif com == 'manga':
                    descriptionStr = '''
                    Get information about a specific manga.
                    Information is provided by MyAnimeList and AniList API.
                    '''
                    embed.add_field(name='Usage', value='`k*manga` `manga`', inline=False)
                    embed.add_field(name='\u2800', value=descriptionStr, inline=False)"""
            elif com == 'waifu':
                descriptionStr = '''
                Shows an image of a random waifu.
                Images are provided by the waifu.pics API.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com in ['cry', 'smug', 'blush', 'nom', 'dance', 'cringe']:
                embed.add_field(name='\u2800', value=f'Shows an anime gif of you {self.animeDict[com]}', inline=False)
            elif com in ['bully', 'cuddle', 'hug', 'kiss', 'pat', 'bonk', 'yeet', 'poke', 'wave']:
                descriptionStr = f'''
                Shows an anime gif of you {self.animeDict[com]} `user`.
                If no user is mentioned, then I will perform the action on you!
                '''
                embed.add_field(name='Usage', value=f'`k*{com}` `user`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'blackjack':
                descriptionStr = '''
                Starts a game of blackjack with me!
                '''
                embed.add_field(name='Shortcuts', value='`bj`', inline=False)
                usageStr = '''
                `k*blackjack` `bet`
                `👆 to Hit`
                `✋ to Stand`
                `2️⃣ to Double Down`
                '''
                embed.add_field(name='Usage', value=usageStr, inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'balance':
                descriptionStr = '''
                Shows your current upa balance.
                '''
                embed.add_field(name='Shortcuts', value='`b`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'daily':
                descriptionStr = '''
                Receive your daily amount of upa (a random amount ranging from 500-1000).
                There is a 5% chance to receive a **metal upa** which grants 500 additional upa!
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com in ['02', 'chika', 'nam', 'ayaya', 'pog', 'sus']:
                embed.add_field(name='\u2800', value=f'Shows ascii art of {self.asciiArtDict[com]}', inline=False)
            elif com == 'eject':
                descriptionStr = '''
                Shows ascii art of a crewmate being ejected.
                If no user is mentioned, then I will eject you!
                '''
                embed.add_field(name='Usage', value='`k*eject` `user`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'setprofile':
                descriptionStr = '''
                Set your osu! profile.
                '''
                embed.add_field(name='Shortcuts', value='`sp`', inline=False)
                embed.add_field(name='Usage', value='`k*setprofile` `username`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'osu':
                descriptionStr = '''
                Shows your osu! statistics. 
                Information is provided by the osu! api.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'serverdropadd':
                descriptionStr = '''
                I will ping you upon a drop due to server activity in this server.
                '''
                embed.add_field(name='Shortcuts', value='`sda`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'serverdropremove':
                descriptionStr = '''
                I will not ping you upon a drop due to server activity in this server.
                '''
                embed.add_field(name='Shortcuts', value='`sdr`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'stats':
                descriptionStr = '''
                Shows Karuta-related statistics for the current server.
                '''
                embed.add_field(name='Shortcuts', value='`s`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'pfp':
                descriptionStr = '''
                Get the profile picture of `user`.
                If no user is specified, I will send your profile picture.
                '''
                embed.add_field(name='Usage', value='`k*pfp` `user`', inline=False)
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'flip':
                descriptionStr = '''
                Flip a coin and get **Heads** or **Tails**.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'roll':
                descriptionStr = '''
                Roll a die and get a number from **1-6**.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'invite':
                descriptionStr = '''
                Get a link to invite me to your server.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            elif com == 'support':
                descriptionStr = '''
                Get an invitation to join Kurisu's support server.
                '''
                embed.add_field(name='\u2800', value=descriptionStr, inline=False)
            else:
                # command does not exist
                await ctx.send(f'{ctx.message.author.mention}, the chosen command does not exist.')
                return
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(
                title='**KurisuBot Commands**',
                description='Use `k*help [command]` for more information on a specific command.', 
                color=0xff0000
            )
            embed.add_field(name='😂 Memes', value='`animeme`', inline=True)
            embed.add_field(
                name='<:ayaya:837496191247450152> Anime', 
                value="""`anime`, `waifu`, `cry`, 
                        `smug`, `blush`, `nom`, 
                        `dance`, `cringe`, `bully`,
                        `cuddle`, `hug`, `kiss`, 
                        `pat`, `bonk`, `yeet`, 
                        `poke`, `wave`""", 
                inline=True
            )
            embed.add_field(name='🎲 Casino', value='`blackjack`', inline=True)
            embed.add_field(name='💰 Economy', value='`daily`\n`balance`', inline=True)
            embed.add_field(
                name='🎨 Ascii Art', 
                value="""`02`, `chika`, `nam`,
                        `ayaya`, `pog`, `uwu`,
                        `sus`, `eject`""",
                inline=True
            )
            embed.add_field(name='<:osu:837390866192007218> osu!', value='`osu`\n`setprofile`', inline=True)
            embed.add_field(name='🎴 Karuta', value='`stats`\n`serverdropadd`\n`serverdropremove`', inline=True)
            embed.add_field(name='💮 Misc.', value='`pfp`, `flip`, `roll`\n`invite`, `support`', inline=True)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Help(client))
