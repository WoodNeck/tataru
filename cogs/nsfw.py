import discord
import functools
from discord.ext import commands
from cogs.utils.http_handler import HTTPHandler
from bs4 import BeautifulSoup

class NSFW():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def 히토미(self, ctx, index):
        if not self.isNSFW(ctx.message.channel):
            await self.alertOnlyInNSFW(ctx.message.channel)
            return
        try:
            index = int(index)
        except:
            self.bot.say("제대로 된 숫자를 인자로 주세용")
            return
        await self.bot.send_typing(ctx.message.channel)
        url = "https://hitomi.la/galleries/{}.html".format(index)
        http = HTTPHandler()
        try:
            response = http.get(url, None)
            html = BeautifulSoup(response.read().decode(), 'html.parser')
            coverDiv = html.find("div", {"class": "cover"})
            coverUrl = "https:{}".format(coverDiv.find("img").get("src"))
            meta = html.find("div", {"class": "gallery"})
            title = self.getMetaInfo(meta.find("h1"))
            artist = self.getAllMetaInfo(meta.find("h2"))
            meta = meta.find("div", {"class": "gallery-info"})
            infoTypes = ["Group", "Type", "Language", "Series", "Characters", "Tags"]
            infoIsMultiple = [False, False, False, False, True, True]
            infoResults = []
            infoLists = meta.find_all("tr")
            for i in range(len(infoTypes)):
                info = infoLists[i]
                if infoIsMultiple[i]:
                    infoResults.append(self.getAllMetaInfo(info.find_all("td")[1]))
                else:
                    infoResults.append(self.getMetaInfo(info.find_all("td")[1]))
            em = discord.Embed(title=title, url=url, colour=0xDEADBF)
            em.set_image(url=coverUrl)
            em.add_field(name="Artist", value=artist)
            for i in range(len(infoTypes)):
                em.add_field(name=infoTypes[i], value=infoResults[i])
            await self.bot.send_message(ctx.message.channel, embed=em)
        except:
            await self.bot.say("페이지가 존재하지 않아용")
    
    def isNSFW(self, channel):
        return channel.name.startswith("nsfw")
    
    def getMetaInfo(self, meta):
        aTag = meta.find('a')
        if aTag:
            return aTag.string.strip()
        else:
            string = meta.string
            if not string:
                string = ""
            return string.strip()
    
    def getAllMetaInfo(self, meta):
        aTags = meta.find_all('a')
        if aTags:
            result = []
            for aTag in aTags:
                result.append(aTag.string.strip())
            return ", ".join(result)
        else:
            string = meta.string
            if not string:
                string = ""
            return string.strip()

    async def alertOnlyInNSFW(self, channel):
        await self.bot.send_message(channel, "`nsfw`채널에서만 사용 가능한 명령어에용")

def setup(bot):
    cog = NSFW(bot)
    bot.add_cog(cog)
