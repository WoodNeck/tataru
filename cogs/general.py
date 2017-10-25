import discord
from discord.ext import commands
from .utils.chat_formatting import escape_mass_mentions, italics, pagify
from random import randint
from random import choice

class General:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def 핑(self):
        await self.bot.say("퐁이에용")

    @commands.command(pass_context=True)
    async def 주사위(self, ctx, number : int = 100):
        author = ctx.message.author
        if number > 1:
            n = randint(1, number)
            await self.bot.say("{}이(가) 주사위를 굴려 🎲{}이(가) 나왔어용".format(author.mention, n))
        else:
            await self.bot.say("{}님 1보다 큰 숫자를 주세용".format(author.mention))

    @commands.command()
    async def 골라줘(self, *choices):
        choices = [escape_mass_mentions(c) for c in choices]
        if len(choices) < 2:
            await self.bot.say("고를 수 있는 항목을 충분히 주세용")
        else:
            await self.bot.say(choice(choices))

    @commands.command()
    async def 초대(self):
        await self.bot.say("https://discordapp.com/oauth2/authorize?client_id=357073005819723777&scope=bot&permissions=-1")

    @commands.command(pass_context=True)
    async def 따귀(self, ctx, args):
        await self.bot.say("{}의 뺨을 후려갈겼어용".format(args))

    @commands.command(pass_context=True)
    async def 사랑해(self, ctx):
        if (randint(0, 1)):
            await self.bot.say("저는 님 친구가 아닙니다")
        else:
            await self.bot.say("저도 사랑해용^^*")

    @commands.command(pass_context=True, hidden=True)
    async def 삼꼬(self, ctx):
        await self.bot.say(":tangerine::hot_pepper::three::straight_ruler:")

def setup(bot):
    general = General(bot)
    bot.add_cog(general)
