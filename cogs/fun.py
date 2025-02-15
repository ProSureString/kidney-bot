# This cog creates all "fun" commands
# Copyright (C) 2023  Alec Jensen
# Full license at LICENSE.md

import discord
from discord.ext import commands
from discord import app_commands
import random
import aiohttp
import logging
import asyncio
import pilcord
from bill import insult
import wikipedia
from faker import Faker


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.scenarios = [
            ['D', 'L', 'W'],
            ['W', 'D', 'L'],
            ['L', 'W', 'D'],
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Fun cog loaded.')

                

    @app_commands.command(name="yomama", description="get a yo mama joke")
    async def yomama(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.yomomma.info/') as r:
                res = await r.json()  # returns dict
                await interaction.response.send_message(res["joke"])

    @app_commands.command(name="dadjoke", description="get dad joked")
    async def dadjoke(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://icanhazdadjoke.com/', headers={"Accept": "application/json"}) as r:
                res = await r.json()
                await interaction.response.send_message(res["joke"])

    @app_commands.command(name="dog", description="dog pic")
    async def dog(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://dog.ceo/api/breeds/image/random') as r:
                res = await r.json()
                await interaction.response.send_message(res["message"])

    @app_commands.command(name="duck", description="get a duck pic")
    async def duck(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/random') as r:
                res = await r.json()
                await interaction.response.send_message(res["url"])

    @app_commands.command(name="cat", description='cat pic')
    async def cat(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://aws.random.cat/meow') as r:
                res = await r.json()
                await interaction.response.send_message(res["file"])

    @app_commands.command(name="meme", description="🤣")
    async def meme(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://meme-api.com/gimme') as r:
                res = await r.json()
                await interaction.response.send_message(res["url"])

    @app_commands.command(name="joke", description="its just a joke??")
    async def joke(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist,explicit&type=single') as r:
                res = await r.json()
                await interaction.response.send_message(res['joke'])

    @app_commands.command(name='8ball', description='get advice on anything')
    async def _8ball(self, interaction: discord.Interaction, question: str):
        responses = ['indeed', 'undoubtedly', 'no', 'dunno', 'indecisive']
        await interaction.response.send_message(f'> {question}\n:8ball: {random.choice(responses)}')

    @app_commands.command(name='rps', description='play rps for money')
    async def rps(self, interaction: discord.Interaction):
        await interaction.response.send_message('Send R for :rock:, send P for :scroll:, send S for :scissors:')

        def check(m):
            return m.content.lower() in ['r', 'p', 's'] and m.channel == interaction.channel and m.author == interaction.user

        message = await self.bot.wait_for('message', check=check, timeout=15)
        if message.content.lower() == 'r':
            player = 0
        elif message.content.lower() == 'p':
            player = 1
        elif message.content.lower() == 's':
            player = 2
        while True:
            computer = random.randint(0, 2)
            if self.scenarios[player][computer] == 'L':
                if random.randint(0, 2) == 0:
                    break
                else:
                    continue
            elif self.scenarios[player][computer] in ['W', 'D']:
                break
        outcome = self.scenarios[player][
            computer]  # Check the table for the outcome

        if outcome == 'W':
            await message.reply('You win! +50 beans')
            await self.bot.addcurrency(message.author, 50, 'wallet')
        elif outcome == 'L':
            await message.reply('I win!')
        elif outcome == 'D':
            await message.reply('Draw!')
    
    @app_commands.command(name='fight_under_this_flag', description='fight under this flag meme')
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def fight_under_this_flag(self, interaction: discord.Interaction, user: discord.Member = None, flag: discord.Attachment = None, flag_url: str = None):
        if user is None and flag is None and flag_url is None:
            image = interaction.user.avatar.url
        elif user is not None and flag is None and flag_url is None:
            image = user.avatar.url
        elif user is None and flag is not None and flag_url is None:
            image = flag.url
        elif user is None and flag is None and flag_url is not None:
            image = flag_url
        else:
            await interaction.response.send_message('Something went wrong, please try again', ephemeral=True)
            return
        await interaction.response.defer()
        a = pilcord.Meme(avatar=image)
        await interaction.followup.send(file=discord.File(await a.fight_under_this_flag(), filename='fight_under_this_flag.png'))
    
    @app_commands.command(name='uwu_discord', description='uwu discord meme')
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def uwu_discord(self, interaction: discord.Interaction, user: discord.Member = None, flag: discord.Attachment = None, flag_url: str = None):
        if user is None and flag is None and flag_url is None:
            image = interaction.user.avatar.url
        elif user is not None and flag is None and flag_url is None:
            image = user.avatar.url
        elif user is None and flag is not None and flag_url is None:
            image = flag.url
        elif user is None and flag is None and flag_url is not None:
            image = flag_url
        else:
            await interaction.response.send_message('Something went wrong, please try again', ephemeral=True)
            return
        await interaction.response.defer()
        a = pilcord.Meme(avatar=image)
        await interaction.followup.send(file=discord.File(await a.uwu_discord(), filename='uwu_discord.png'))
    
    @app_commands.command(name='rip', description='rip meme')
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def rip(self, interaction: discord.Interaction, user: discord.Member = None, flag: discord.Attachment = None, flag_url: str = None):
        if user is None and flag is None and flag_url is None:
            image = interaction.user.avatar.url
        elif user is not None and flag is None and flag_url is None:
            image = user.avatar.url
        elif user is None and flag is not None and flag_url is None:
            image = flag.url
        elif user is None and flag is None and flag_url is not None:
            image = flag_url
        else:
            await interaction.response.send_message('Something went wrong, please try again', ephemeral=True)
            return
        await interaction.response.defer()
        a = pilcord.Meme(avatar=image)
        await interaction.followup.send(file=discord.File(await a.rip(), filename='rip.png'))
    
    @app_commands.command(name='synonym', description='get a synonym')
    async def synonym(self, interaction: discord.Interaction, word: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.datamuse.com/words?rel_syn={word}') as r:
                res = await r.json()
                words = []
                for i in res:
                    if len(words) < 10:
                        words.append(i['word'])
                    else: break
                await interaction.response.send_message(f"Synonyms for {word}:\n{', '.join(words)}")
    
    @app_commands.command(name='antonym', description='get an antonym')
    async def antonym(self, interaction: discord.Interaction, word: str):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://api.datamuse.com/words?rel_ant={word}') as r:
                res = await r.json()
                words = []
                for i in res:
                    if len(words) < 10:
                        words.append(i['word'])
                    else: break
                await interaction.response.send_message(f"Antonyms for {word}:\n{', '.join(words)}")
    
    @app_commands.command(name='shakespearean-insult', description='get a shakespearean insult')
    async def shakespearean_insult(self, interaction: discord.Interaction):
        await interaction.response.send_message(insult())
    
    @app_commands.command(name='wikipedia', description='get a wikipedia article')
    async def wikipedia(self, interaction: discord.Interaction, query: str):
        try:
            await interaction.response.send_message(wikipedia.summary(query, sentences=2))
        except wikipedia.exceptions.DisambiguationError as e:
            options = []
            for i in e.options:
                if len(options) < 10:
                    options.append(i)
                else: break
            await interaction.response.send_message(f"Could not determine what you meant, please be more specific. Here are some options:\n{', '.join(options)}", ephemeral=True)

    @app_commands.command(name="fake-info", description="get fake info")
    async def fake_info(self, interaction: discord.Interaction):
        fake = Faker()
        await interaction.response.send_message(f"{fake.name()}\n{fake.address()}")


async def setup(bot):
    await bot.add_cog(Fun(bot))
