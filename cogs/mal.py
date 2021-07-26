import discord
from discord.ext import commands
import aiohttp
import asyncio
from jikanpy import AioJikan

class Mal(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('MAL cog is online.')

    # Commands
    @commands.command(aliases=['a'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def anime(self, ctx, *, animeTitle=None):
        if animeTitle is None:
            await ctx.send(f'{ctx.author.mention}, you must specify an anime to lookup.')
            return
        if len(animeTitle) > 100:
            await ctx.send(f'{ctx.author.mention}, the title of this anime is too long.')
            return
        pages = []
        buttons = [u'\u2B05', u'\u27A1'] # arrow_left, arrow_right
        # get anime listing
        async with AioJikan() as aioJikan:
            searchDict = await aioJikan.search(search_type='anime', query=animeTitle, page=1)
            animeList = searchDict['results']
            numAnime = len(animeList) # num of anime on current page
            numPages = (numAnime + 4) // 5 # num of pages in embed. want 5 anime per page
            totalAnimeIdx = 0
            #print(f'numAnime: {numAnime}')
            #print(f'numPages: {numPages}')
            for pageIdx in range(numPages):
                embed = discord.Embed(title='Anime Listing', description='**Select an anime by entering its number.**', color=0xff0000)
                animeListStr = ''
                pageAnimeIdx = 0
                while totalAnimeIdx < numAnime and pageAnimeIdx < 5:
                    animeListStr += '{}. {}\n'.format(totalAnimeIdx + 1, animeList[totalAnimeIdx]['title'])
                    totalAnimeIdx += 1
                    pageAnimeIdx += 1

                embed.add_field(name='\u200b', value=animeListStr+'\u200b', inline=False)
                embed.set_footer(text=f'Page {pageIdx + 1}/{numPages}')
                pages.append(embed)

        # first page and add buttons (add error checking: bad search query, no pages)
        curPageIdx = 0
        msg = await ctx.send(embed=pages[curPageIdx])
        for button in buttons:
            await msg.add_reaction(button)

        # checks for on_reaction_add and on_message
        def message_check(inputMsg):
            # Only accept messages from:
            # The person who invoked the command and in the same channel.
            # ---- check for valid index. if it is another k*anime command, end this one (await or sleep if needed)----
            # check if another k*anime command:
            content = inputMsg.content
            if content.startswith('k*anime') or content.startswith('k*a'):
                raise asyncio.TimeoutError # will this reach? goal is to end this message life
            ok = False
            try: 
                # remove all whitespace from inputMsg
                chosenIdx = int(''.join(content.split()))
                if 1 <= chosenIdx and chosenIdx <= numAnime:
                    ok = True
            except ValueError as e:
                #print(f'Value Error: {e}')
                pass
            return (ok and (inputMsg.author.id == ctx.author.id) and (inputMsg.channel.id == ctx.channel.id))
        
        def reaction_check(reaction, user):
            # Only accept reactions from:
            # The person who invoked the command and on the bot's message.
            return reaction.message.id == msg.id and user.id == ctx.author.id
        
        # handle page navigation
        while True:
            try:
                m = self.client.wait_for('message', check=message_check)
                r = self.client.wait_for('reaction_add', check=reaction_check)
                done, pending = await asyncio.wait([m, r], timeout=10, return_when=asyncio.FIRST_COMPLETED)
                # does the timeout reset? i think problem is that its in a while true.
                for p in pending:
                    # Cancel the pending tasks that weren't completed
                    p.cancel()
                    
                if done:
                    # At least one task was completed
                    response = done.pop().result()
                    if isinstance(response, discord.Message):
                        # Check if the task returned a discord.Message.
                        chosenIdx = int(''.join(response.content.split())) - 1
                        #print(f'chosenIdx: {chosenIdx}')
                        chosenAnime = animeList[chosenIdx]
                        animeTitle = chosenAnime['title']
                        animeImgUrl = chosenAnime['image_url']
                        animeId = chosenAnime['mal_id']
                        animeUrl = 'https://myanimelist.net/anime/{}'.format(animeId)
                        animeStartDate = chosenAnime['start_date']
                        if animeStartDate is None:
                            animeStartDate = '-'
                        else:
                            animeStartDate = animeStartDate.split('T')[0]
                        animeEndDate = chosenAnime['end_date']
                        if animeEndDate is None:
                            animeEndDate = '-'
                        else:
                            animeEndDate = animeEndDate.split('T')[0]
                        animeScore = chosenAnime['score']
                        animeType = chosenAnime['type']
                        #animeEpisodeCnt = chosenAnime['episodes'] this will be from MAL. changed to use AniList below.
                        aniListId = -1
                        totalEpisodeCnt = -1
                        animeStatus = '-'
                        secUntilAiring = 0
                        airingEpisodeNumber = -1
                        '''
                        this is for using myanimelist and datetime module to calculate current status.
                        now this cog uses the AniList API which provides the status.
                        now = datetime.datetime.now()
                        year = '{:02d}'.format(now.year)
                        month = '{:02d}'.format(now.month)
                        day = '{:02d}'.format(now.day)
                        curDate = '{}-{}-{}'.format(year, month, day)
                        if (animeStartDate != '-' and curDate < animeStartDate) or (animeStartDate == '-' and animeEndDate == '-'):
                            animeStatus = 'Upcoming'
                        elif animeEndDate != '-' and curDate > animeEndDate:
                            animeStatus = 'Finished'
                        else:
                            animeStatus = 'Airing'
                        '''
                        # changed to use the search page synopsis. the full one is too long for discord ...
                        animeSynopsis = chosenAnime['synopsis']
                        if animeSynopsis is None or animeSynopsis == 'None' or animeSynopsis == '':
                            animeSynopsis = '-'
                        # to get the full synopsis, have to navigate to the MAL page of the anime, rather than its search summary
                        '''
                        async with AioJikan() as aio_jikan2:
                            chosenAnimePage = await aio_jikan2.anime(animeId)
                            animeSynopsis = chosenAnimePage['synopsis']
                        if animeSynopsis is None or animeSynopsis == 'None':
                            animeSynopsis = '-'
                        else:
                            animeSynopsis = animeSynopsis.partition('[Written by MAL Rewrite]')[0]
                            if len(animeSynopsis) >= 1024:
                                # an embed's value cannot exceed 1024 characters
                                animeSynopsis = animeSynopsis[0:1021] + '...'
                        '''
                        #print(f'Title: {animeTitle}')
                        # send a request to AniList API to convert MAL id to AniList id
                        # refer to AniList API documentation for query
                        query = '''
                        query($id: Int, $type: MediaType) {
                            Media(idMal: $id, type: $type) {
                                id
                                episodes
                                status
                                nextAiringEpisode {
                                    timeUntilAiring
                                    episode
                                }
                            }
                        }
                        '''
                        variables = {
                            'id': animeId, # MAL ID of chosenAnime
                            'type': "ANIME"
                        }
                        url = 'https://graphql.anilist.co'
                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, json={'query': query, 'variables': variables}) as r:
                                js = await r.json()
                                #print(js)
                                #print(js['data']['Media']['status'])
                                #print(f"timeUntilAiring (sec): {js['data']['Media']['nextAiringEpisode']['timeUntilAiring']}")
                                aniListId = js['data']['Media']['id']
                                totalEpisodeCnt = js['data']['Media']['episodes']
                                animeStatus = js['data']['Media']['status']
                                if animeStatus == 'RELEASING':
                                    secUntilAiring = js['data']['Media']['nextAiringEpisode']['timeUntilAiring']
                                    airingEpisodeNumber = js['data']['Media']['nextAiringEpisode']['episode']
                        # create custom status
                        if animeStatus == 'RELEASING':
                            animeStatus = 'AIRING'
                        elif animeStatus == 'NOT_YET_RELEASED':
                            animeStatus = 'UPCOMING'
                        # create the anime's embed
                        embed = discord.Embed(title=animeTitle, color=0xff0000)
                        embed.set_thumbnail(url=animeImgUrl)
                        embed.add_field(name="Score", value=animeScore, inline=True)
                        if totalEpisodeCnt is not None and totalEpisodeCnt != -1:
                            embed.add_field(name="Episodes", value=totalEpisodeCnt, inline=True)
                        elif airingEpisodeNumber != -1:
                            embed.add_field(name="Episodes", value=airingEpisodeNumber, inline=True)
                        else:
                            embed.add_field(name="Episodes", value='-', inline=True)
                        embed.add_field(name="Type", value=animeType, inline=True)
                        embed.add_field(name="Started", value=animeStartDate, inline=True)
                        embed.add_field(name="Ended", value=animeEndDate, inline=True)
                        embed.add_field(name="Status", value=animeStatus, inline=True)
                        embed.add_field(name="Synopsis", value=animeSynopsis, inline=False)
                        if aniListId != -1:
                            embed.add_field(name='AniList Link', value=f'https://anilist.co/anime/{aniListId}', inline=False)
                        embed.add_field(name='MyAnimeList Link', value=f'[{animeUrl}]({animeUrl})', inline=False)
                        # special case: if this anime is currently airing, set embed footer to time until next ep airs (days/hr/mn)
                        if animeStatus == 'AIRING':
                            embed.set_footer(text=f'Episode {airingEpisodeNumber} airs in {self.display_time(secUntilAiring)}')
                        await ctx.send(embed=embed)
                        # user has successfully picked an anime and received a result. message can now expire.
                        raise asyncio.TimeoutError
                    else:
                        # Otherwise it is a tuple of reaction and user.
                        emote = response[0].emoji
                        prevPageIdx = curPageIdx
                        if emote == u'\u2B05':
                            # arrow_left
                            if curPageIdx > 0:
                                curPageIdx -= 1
                        elif emote == u'\u27A1':
                            # arrow_right
                            if curPageIdx < numPages - 1:
                                curPageIdx += 1
                        # remove user reactions
                        #for button in buttons:
                        #    await msg.remove_reaction(button, ctx.author)
                        if curPageIdx != prevPageIdx:
                            await msg.edit(embed=pages[curPageIdx])
                else:
                    raise asyncio.TimeoutError
            except Exception as e:
                #print(f'Error in mal.py: {e}')
                embed = pages[curPageIdx]
                embed.set_footer(text='The listing has expired.')
                await msg.edit(embed=embed)
                break # if we dont break here, the bot will keep listening for reactions.
                #await msg.clear_reactions()

    # Other methods
    def display_time(self, seconds, granularity=3):
        intervals = (
        ('days', 86400),    # 60 * 60 * 24
        ('hours', 3600),    # 60 * 60
        ('minutes', 60),
        )
        result = []
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])

def setup(client):
    client.add_cog(Mal(client))
