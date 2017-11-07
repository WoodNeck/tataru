import discord
from os import walk
from random import randint
from random import choice
from discord.ext import commands

class Jjal:
    def __init__(self, bot):
        self.bot = bot
        self.kejang = []
        for (dirpath, dirnames, filenames) in walk("./data/kejang"):
            self.kejang.extend(filenames)
            break

        self.kejangList = []
        cnt = 0
        prefix = ("🔹", "🔸")
        tempList = []
        for name in self.kejang:
            cnt += 1
            toAppend = prefix[cnt % 2] + name.split(".")[0]
            postfix = 0
            for char in name:
                if ord(char) < 128:
                    postfix += 1
            toAppend = "{:　<{width}}".format(toAppend, width=8)
            toAppend += " " * postfix
            tempList.append(toAppend)
            if (len(tempList) == 4):
                self.kejangList.append(tuple(tempList))
                tempList.clear()
        if (len(tempList)):
            self.kejangList.append(tuple(tempList))

    @commands.command(pass_context=True)
    async def 케장(self, ctx, args):
        if (args == ""):
            await self.bot.say("`케장콘 목록` 명령으로 목록을 확인할 수 있어용")
        elif (args == "목록"):
            desc = ""
            for item in self.kejangList:
                desc += "".join(item)
                desc += "\n"
            await self.bot.say("```가능한 케장콘 목록이에용\n{}```".format(desc))
        else:
            for name in self.kejang:
                if name.split(".")[0] == args:
                    with open("./data/kejang/{}".format(name), "rb") as f:
                        await self.bot.send_file(ctx.message.channel, f)
                        return
            await self.bot.say("해당 케장콘이 목록에 존재하지 않아용")

def setup(bot):
    cog = Jjal(bot)
    bot.add_cog(cog)
