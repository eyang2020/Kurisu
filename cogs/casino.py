import os
import asyncio
import discord
from discord.ext import commands
from discord.ext import menus
import pymongo
from datetime import datetime
import random

MONGODB_AUTH = os.environ['MONGODB_AUTH']
cluster = pymongo.MongoClient(MONGODB_AUTH)

db = cluster.test
collection = db['Economy']

class BlackjackMenu(menus.Menu):
    suit = ['♡', '♢', '♤', '♧']
    val = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    def __init__(self, user, bet, balance):
        super().__init__(timeout=30.0, delete_message_after=False)
        self.user = user
        self.bet = bet
        self.balance = balance
        # cnt[i][j] represents the number times the card of suit[i] and val[j] has been drawn
        # blackjack will use 6 decks, so max of cnt[i][j] will be 6
        self.cnt = [[0 for j in range(13)] for i in range(4)]
        self.userSum = 0
        self.userStr = ''
        self.userSoftHand = False # True if user has an ace that is 11
        self.dealerSum = 0
        self.dealerStr = ''
        self.dealerSoftHand = False
        # this represents the dealer's facedown card
        self.facedownCard = None

    async def show_card(self):
        # show dealer's facedown card
        self.dealerSum += int(self.facedownCard[0])
        self.dealerStr = '{}{}'.format(self.dealerStr[:-1], self.facedownCard[1])

    async def draw(self, drawer):
        # drawer = 0 -> user, drawer = 1 -> dealer
        # helper function to draw a random card from six 52 card decks
        suitIdx = random.randint(0, 3)
        valIdx = random.randint(0, 12) 
        while(self.cnt[suitIdx][valIdx] >= 6):
            suitIdx = random.randint(0, 3)
            valIdx = random.randint(0, 12)
        self.cnt[suitIdx][valIdx] += 1
        cardVal = 0 # ex: 3
        cardName = '' # ex: 3♡
        if valIdx == 0:
            # ace needs to be handled specially since they are 1 or 11 (max is one 11)
            if drawer == 0:
                if self.userSum + 11 <= 21:
                    cardVal = 11
                    self.userSoftHand = True
                else:
                    cardVal = 1
            else:
                if self.dealerSum + 11 <= 21:
                    cardVal = 11
                    self.dealerSoftHand = True
                else:
                    cardVal = 1
        elif (valIdx == 10) or (valIdx == 11) or (valIdx == 12):
            cardVal = 10
        else:
            cardVal = int(self.val[valIdx])
        cardName = '{}{}'.format(self.val[valIdx], self.suit[suitIdx])
        # check bust
        if drawer == 0 and self.userSum + cardVal > 21 and self.userSoftHand:
            self.userSum -= 10 # set the 11-ace to a 1-ace
            self.userSoftHand = False
        elif drawer == 1 and self.dealerSum + cardVal > 21 and self.dealerSoftHand:
            self.dealerSum -= 10 # set the 11-ace to a 1-ace
            self.dealerSoftHand = False
        return (cardVal, cardName)

    async def game_lose(self, bust=False):
        # update balance
        doc = collection.find_one({'userId': self.user.id})
        newBalance = doc['upa'] - self.bet
        collection.update_one({'userId': self.user.id}, {'$set': {'upa': newBalance}})
        # helper function to create the embed for lost game
        embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
        embed.add_field(name=f'Dealer: {self.dealerSum}', value=self.dealerStr, inline=False)
        if bust:
            embed.add_field(name='Bust', value=f'You lost **{self.bet}** upa', inline=False)
        else:
            embed.add_field(name='Lost', value=f'You lost **{self.bet}** upa', inline=False)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f'Bet: {self.bet} upa')
        return embed

    async def game_win(self, blackjack=False):
        # helper function to create the embed for won game
        embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
        embed.add_field(name=f'Dealer: {self.dealerSum}', value=self.dealerStr, inline=False)
        # if natural (blackjack) is True, then payout has a 1.5 multiplier
        doc = collection.find_one({'userId': self.user.id})
        newBalance = doc['upa']
        if blackjack:
            payout = round(self.bet * 1.5)
            newBalance += payout
            embed.add_field(name='Blackjack (x1.5 multiplier)', value=f'You won **{payout}** upa', inline=False)
        else:
            newBalance += self.bet
            embed.add_field(name='Win', value=f'You won **{self.bet}** upa', inline=False)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f'Bet: {self.bet} upa')
        # update balance in database
        collection.update_one({'userId': self.user.id}, {'$set': {'upa': newBalance}})
        return embed

    async def game_tie(self):
        # helper function to create the embed for tied game
        embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
        embed.add_field(name=f'Dealer: {self.dealerSum}', value=self.dealerStr, inline=False)
        embed.add_field(name='Push', value=f'Your bet of **{self.bet}** upa has been returned', inline=False)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f'Bet: {self.bet} upa')
        return embed

    async def hit(self, doubleDown=False):
        # helper function to simulate hit
        # hit: user draws another card     
        card = await self.draw(0)
        self.userSum += card[0]
        self.userStr = '{}-{}'.format(self.userStr, card[1])
        if self.userSum > 21:
            self.stop()
            await self.show_card()
            await self.message.edit(embed=await self.game_lose(bust=True))
        elif self.userSum == 21:
            # user now automatically stands
            # stop listening for reactions
            self.stop()
            embedList = await self.stand()
            for em in embedList:
                await self.message.edit(embed=em)
                await asyncio.sleep(2)
            #print('User now automatically stands.')
        else:
            # update the embed
            embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
            embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
            embed.add_field(name=f'Dealer: {self.dealerSum} + ?', value=self.dealerStr, inline=False)
            embed.timestamp = datetime.utcnow()
            embed.set_footer(text=f'Bet: {self.bet} upa')
            await self.message.edit(embed=embed)
            # if user doubled-down, stand automatically
            if doubleDown:
                self.stop()
                embedList = await self.stand()
                await asyncio.sleep(2)
                for em in embedList:
                    await self.message.edit(embed=em)
                    await asyncio.sleep(2)

    async def stand(self):
        # helper function to update the embed of stand (dealer play) by returning a list of embeds
        embedList = []
        # stand: dealer shows facedown card. hit if <= 16, stand on >= 17.
        await self.show_card()
        embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
        embed.add_field(name=f'Dealer: {self.dealerSum}', value=self.dealerStr, inline=False)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f'Bet: {self.bet} upa')
        embedList.append(embed)
        # hit while <= 16, stand once >= 17
        while self.dealerSum <= 16:
            card = await self.draw(1)
            self.dealerSum += int(card[0])
            self.dealerStr = '{}-{}'.format(self.dealerStr, card[1])
            embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
            embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
            embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
            embed.add_field(name=f'Dealer: {self.dealerSum}', value=self.dealerStr, inline=False)
            embed.timestamp = datetime.utcnow()
            embed.set_footer(text=f'Bet: {self.bet} upa')
            embedList.append(embed)
        # check final result of game
        if self.dealerSum > 21 or (self.userSum > self.dealerSum):
            embedList.append(await self.game_win())
        elif self.userSum == self.dealerSum:
            embedList.append(await self.game_tie())
        else:
            embedList.append(await self.game_lose())
        return embedList

    async def send_initial_message(self, ctx, channel):
        # first deal
        card = await self.draw(0)
        self.userSum = card[0]
        self.userStr = card[1]
        card = await self.draw(1)
        self.dealerSum = card[0]
        self.dealerStr = card[1]
        # second deal
        card = await self.draw(0)
        self.userSum += card[0]
        self.userStr = '{}-{}'.format(self.userStr, card[1])
        self.facedownCard = await self.draw(1)
        self.dealerStr = '{}-{}'.format(self.dealerStr, '?')
        # create starting embed
        embed = discord.Embed(title=':small_orange_diamond: Blackjack :small_orange_diamond:', color=0xff0000)
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name=f'You: {self.userSum}', value=self.userStr, inline=False)
        embed.add_field(name=f'Dealer: {self.dealerSum} + ?', value=self.dealerStr, inline=False)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f'Bet: {self.bet} upa')
        msg = await channel.send(embed=embed)
        # check for naturals (blackjacks)
        if self.userSum == 21:
            await self.show_card()
            if self.dealerSum + self.facedownCard[0] == 21:
                # tie/push
                await asyncio.sleep(3)
                await msg.edit(embed=await self.game_tie())
                self.stop()
                return
            else:
                # user has blackjack but dealer does not
                await asyncio.sleep(3)
                await msg.edit(embed=await self.game_win(blackjack=True))
                self.stop()
                return
        elif self.dealerSum + self.facedownCard[0] == 21:
            # dealer has blackjack but user does not
            await self.show_card()
            await asyncio.sleep(3)
            await msg.edit(embed=await self.game_lose())
            self.stop()
            return
        # no naturals, game continues
        return msg

    @menus.button('👆')
    async def on_point_up_2(self, payload):
        if self.user.id == payload.user_id:
            await self.hit()

    @menus.button('✋')
    async def on_raised_hand(self, payload):
        # stand: dealer shows facedown card. hit if <= 16, stand on >= 17.
        # stop listening for reactions
        
        # if a bug arises where menus are not user-specific,
        # add a check for these two ids
        #print(f'payloadID: {payload.user_id}')
        #print(f'userID: {self.user.id}')

        if self.user.id == payload.user_id:
            self.stop()
            embedList = await self.stand()
            for em in embedList:
                await self.message.edit(embed=em)
                await asyncio.sleep(2)
    
    def _cannotDoubleDown(self):
        # returns True if user can double down
        # False if user cannot double down
        #print('Checking skip function...')
        return (self.balance < self.bet * 2)

    @menus.button('2️⃣', skip_if=_cannotDoubleDown)
    async def on_two(self, payload):
        # double-down: user doubles their initial bet, hits once more then stands
        # check if user has the funds to double their initial bet
        if self.user.id == payload.user_id:
            if self.bet * 2 <= self.balance:
                self.stop()
                self.bet *= 2
                await self.hit(doubleDown=True)

class Casino(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        print('Casino cog is online.')

    # Commands
    @commands.command(aliases=['bj'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blackjack(self, ctx, bet=None):
        user = ctx.message.author
        userId = user.id
        try:
            bet = int(bet)
        except:
            await ctx.send(f'{user.mention}, place your bet using **k*blackjack** [**bet**].')
            return
        doc = collection.find_one({'userId': userId})
        if doc is None:
            # insert a new document for this user and set the balance to 0
            collection.update_one({'userId': userId}, {'$set': {'upa': 0}}, upsert=True)
        # validate bet amount
        balance = doc['upa']
        if bet > balance:
            await ctx.send(f'{user.mention}, you do not have the necessary funds to make this bet.')
        elif bet <= 0:
            await ctx.send(f'{user.mention}, place a bet starting at 1 upa.')
        else:
            # play blackjack
            try:
                menu = BlackjackMenu(user, bet, balance)
                await menu.start(ctx) 
            except:
                pass

def setup(client):
    client.add_cog(Casino(client))
