import discord
from discord.ext import commands
from discord.ext import menus

# a class representing the embed the user interacts with
class EffortMenu(menus.Menu):
    def __init__(self, user, imageUrl, isInjured, effortVal, baseVal, styleVal):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.user = user
        self.imageUrl = imageUrl
        self.isInjured = isInjured
        self.effortVal = effortVal
        self.baseVal = baseVal
        self.styleVal = styleVal

    async def send_initial_message(self, ctx, channel):
        # create the condition question embed only if the style == 0
        qualityStr = '''```css\n1. Mint ★★★★\n2. Excellent ★★★☆\n3. Good ★★☆☆\n4. Poor ★☆☆☆\n5. Damaged ☆☆☆☆```'''
        effortEmbedQuestion = discord.Embed(title='Effort Visualizer', color=0xff0000)
        effortEmbedQuestion.add_field(name='Select the card\'s current quality: ', value=qualityStr)
        effortEmbedQuestion.set_thumbnail(url=self.imageUrl)  
        return await channel.send(embed=effortEmbedQuestion)

    # create resulting effort embed
    async def getEffortEmbed(self, starsRemaining):
        # create the result embed
        effortEmbed = discord.Embed(title='Effort Visualizer', color=0xff0000)
        # check if card is injured
        if self.isInjured:
            # user healthy effort estimate for the calculations below
            self.effortVal *= 5
            text = str(f'''```css\n{self.effortVal} Uninjured effort```''')
            effortEmbed.add_field(name='Health: Injured', value=text, inline=False)

        # format and create effort embed
        mintEffort = round(self.effortVal * ((1.89)**starsRemaining))
        # with each upgrade, base value doubles
        self.baseVal = self.baseVal * (2 ** starsRemaining)
        frameStyle = int(round(self.baseVal * 0.75)) # mystic = frame
        frameWellness = int(round(frameStyle * 0.25))
        dyeStyle = int(round(self.baseVal * 0.2))
        dyeWellness = int(round(dyeStyle * 0.25))
        frameDyeStyle = int(round(self.baseVal * 0.95))
        frameDyeWellness = int(round(frameDyeStyle * 0.25))
        frameMysticStyle = int(round(self.baseVal * 1.5))
        frameMysticWellness = int(round(frameMysticStyle * 0.25))
        # create total efforts
        effortFrame = mintEffort + frameStyle + frameWellness
        effortDye = mintEffort + dyeStyle + dyeWellness
        effortFrameDye = mintEffort + frameDyeStyle + frameDyeWellness
        effortFrameMystic = mintEffort + frameMysticStyle + frameMysticWellness
        effortEmbed.set_thumbnail(url=self.imageUrl)        
        # check what the card already has
        if self.styleVal == frameStyle: 
            # could be frame or mystic dye
            resultStr = f'''```css\n{effortDye} Framed & Dyed\n{effortFrame} Framed & Mystic Dyed```'''
            effortEmbed.add_field(name='Status: Framed or Mystic Dyed', value=resultStr)
        elif self.styleVal == dyeStyle:
            # regular dye
            # for mystic, must subtract the reg dye
            resultStr = f'''```css\n{effortFrame} Framed & Dyed\n{mintEffort + (frameStyle + frameWellness - (dyeStyle + dyeWellness))} Framed & Mystic Dyed```'''
            effortEmbed.add_field(name='Status: Dyed', value=resultStr)
        elif self.styleVal == frameDyeStyle:
            # frame and dye
            # for mystic, must subtract the reg dye
            resultStr = f'''```css\n{mintEffort + (frameStyle + frameWellness - (dyeStyle + dyeWellness))} Framed & Mystic Dyed```'''
            effortEmbed.add_field(name='Status: Framed & Dyed', value=resultStr)
        elif self.styleVal == frameMysticStyle:
            # frame and mystic dye
            effortEmbed.add_field(name='Status: Framed & Mystic Dyed', value='The effort on this card is maxed out!')
        else:
            # nothing detected, show all possibilities
            if starsRemaining == 0:
                resultStr = f'''```css\n{effortDye} Dyed\n{effortFrame} Framed\n{effortFrameDye} Framed & Dyed\n{effortFrameMystic} Framed & Mystic Dyed```'''
            else:
                resultStr = f'''```css\n{mintEffort} Mint effort\n{effortDye} Dyed\n{effortFrame} Framed\n{effortFrameDye} Framed & Dyed\n{effortFrameMystic} Framed & Mystic Dyed```'''
            effortEmbed.add_field(name='Status: Unframed & Undyed', value=resultStr)
        # add a warning about accuracy
        effortEmbed.set_footer(text='Within a 1% margin of error')
        # send the embed
        return effortEmbed

    @menus.button('1️⃣')
    async def on_one(self, payload):
        if self.user.id == payload.user_id:
            self.stop()
            embed = await self.getEffortEmbed(0)
            await self.message.edit(embed=embed)

    @menus.button('2️⃣')
    async def on_two(self, payload):
        if self.user.id == payload.user_id:
            self.stop()
            embed = await self.getEffortEmbed(1)
            await self.message.edit(embed=embed)

    @menus.button('3️⃣')
    async def on_three(self, payload):
        if self.user.id == payload.user_id:
            self.stop()
            embed = await self.getEffortEmbed(2)
            await self.message.edit(embed=embed)

    @menus.button('4️⃣')
    async def on_four(self, payload):
        if self.user.id == payload.user_id:
            self.stop()
            embed = await self.getEffortEmbed(3)
            await self.message.edit(embed=embed)

    @menus.button('5️⃣')
    async def on_five(self, payload):
        if self.user.id == payload.user_id:
            self.stop()
            embed = await self.getEffortEmbed(4)
            await self.message.edit(embed=embed)

class EffortCalc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('EffortCalc cog is online.')

    @commands.Cog.listener()
    async def on_message(self, message):
        # message represents the user's invocation of kwi
        content = message.content
        try:
            if content.split()[0].lower() == 'kwi':
                user = message.author
                channel = message.channel
                # valid message, now check cooldowns
                bucket = self.cd_mapping.get_bucket(message)
                retry_after = bucket.update_rate_limit()
                # not on cd
                if not retry_after:
                    def message_check(inputMsg):
                        # Only accept the message that includes The "Worker Details" embed from KarutaBot and in the same channel.
                        ok = (inputMsg.author.id == 646937666251915264) and (inputMsg.channel.id == channel.id)
                        if not ok:
                            return False
                        try:
                            '''
                            # check if original command by user was invalid
                            if 'code is invalid' in inputMsg.content:
                                invalidCommand = True
                                return False
                            '''
                            # check if this is a worker details embed
                            karutaEmbed = inputMsg.embeds[0].to_dict()
                            ok = (karutaEmbed['title'] == 'Worker Details')
                        except:
                            ok = False
                        return ok
                    try:
                        # karutaMsg represents Karuta's Worker Details message
                        # timeout = 5 (listen for 5 sec) since currently as of 5/2/2021, there is a 5 second cooldown on kwi
                        karutaMsg = await self.client.wait_for('message', check=message_check, timeout=5)
                        # parse karuta's worker detail embed
                        karutaMsg = karutaMsg
                        karutaEmbed = karutaMsg.embeds[0].to_dict()
                        desc = karutaEmbed['description']
                        imageUrl = karutaEmbed['thumbnail']['url']
                        isInjured = ('Injured' in desc)
                        parsedList = desc.split()
                        effortVal = 0
                        baseVal = 0
                        styleVal = 0
                        for idx, val in enumerate(parsedList):
                            if val == 'Effort':
                                effortVal = int(parsedList[idx + 2][2:-2])
                            elif val == 'Base':
                                baseVal = int(parsedList[idx - 1])
                            elif val == 'Style':
                                styleVal = int(parsedList[idx - 2])
                        # create a menu object.
                        menu = EffortMenu(user, imageUrl, isInjured, effortVal, baseVal, styleVal)
                        if styleVal == 0:
                            ctx = await self.client.get_context(message)
                            await menu.start(ctx) 
                        else:
                            # otherwise we know the card is mint since it has some style modifier
                            embed = await menu.getEffortEmbed(0)
                            return await channel.send(embed=embed)
                    except Exception as e1:
                        #print(Parsing error: {e1})
                        pass
        except Exception as e2:
            #print(f'Invalid message error: {e2}')
            pass

def setup(client):
    client.add_cog(EffortCalc(client))
