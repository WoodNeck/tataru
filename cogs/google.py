import discord
import urllib
from discord.ext import commands
from .sound import Sound
from cogs.utils.session import Session
from cogs.utils.music_player import MusicPlayer
from cogs.utils.http_handler import HTTPHandler
from bs4 import BeautifulSoup

class Google:
    def __init__(self, bot):
        self.bot = bot
        self.headers = {}
        self.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        self.headers["upgrade-insecure-requests"] = 1
        self.headers["x-chrome-uma-enabled"] = 1
        self.headers["cache-control"] = "max-age=0"

    @commands.command(pass_context=True)  
    async def 이미지(self, ctx, *args):
        self.bot.send_typing(ctx.message.channel)
        searchText = " ".join([arg for arg in args])
        encText = urllib.parse.quote(searchText.encode('utf-8'))
        url = "https://m.youtube.com/search?q={}&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg".format(encText)
        html = self.getHtml(url)
        images = self.findAllImages(html)
        if not images:
            self.bot.say("검색 결과가 없어용")
            return
        session = Session()
        session.set(images)
        image = session.first()
        
        em = discord.Embed(colour=0xDEADBF)
        em.set_image(url=image)
        em.set_footer(text="{}/{}".format(session.index() + 1, session.count()))
        msg = await self.bot.send_message(ctx.message.channel, embed=em)

        emojiMenu = ["⬅", "➡", "❌"]
        for emoji in emojiMenu:
            await self.bot.add_reaction(msg, emoji)

        while True:
            res = await self.bot.wait_for_reaction(emojiMenu, timeout=30, user=ctx.message.author, message=msg)
            if not res:
                for emoji in emojiMenu:
                    await self.bot.remove_reaction(msg, emoji, self.bot.user)
                    await self.bot.remove_reaction(msg, emoji, ctx.message.author)
                return
            elif res.reaction.emoji == "⬅":
                image = session.prev()
                em.set_image(url=image)
                em.set_footer(text="{}/{}".format(session.index() + 1, session.count()))
                await self.bot.edit_message(msg, embed=em)
                await self.bot.remove_reaction(msg, "⬅", ctx.message.author)
            elif res.reaction.emoji == "➡":
                image = session.next()
                em.set_image(url=image)
                em.set_footer(text="{}/{}".format(session.index() + 1, session.count()))
                await self.bot.edit_message(msg, embed=em)
                await self.bot.remove_reaction(msg, "➡", ctx.message.author)
            elif res.reaction.emoji == "❌":
                await self.bot.delete_message(msg)
                await self.bot.delete_message(ctx.message)
                return

    def getHtml(self, url):
        http = HTTPHandler()
        response = http.get(url, self.headers)
        html = str(response.read())
        return html

    def findNextImage(self, s):
        start_line = s.find('rg_di')
        if start_line == -1:
            end_quote = 0
            link = "no_links"
            return link, end_quote
        else:
            start_line = s.find('"class="rg_meta"')
            start_content = s.find('"ou"',start_line+1)
            end_content = s.find(',"ow"',start_content+1)
            if start_content == -1 or end_content == 0:
                end_quote = 0
                link = "no_links"
                return link, end_quote
            content_raw = str(s[start_content+6:end_content-1])
            return content_raw, end_content

    def findAllImages(self, page):
        items = []
        while True:
            item, end_content = self.findNextImage(page)
            if item == "no_links":
                break
            else:
                flag = False
                possiblePostfix = [".jpg", ".png"]
                for postfix in possiblePostfix:
                    if item.lower().endswith(postfix):
                        flag = True
                if flag:
                    items.append(item)
                page = page[end_content:]
        return items

    @commands.command(pass_context=True)
    async def 유튜브(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("검색어를 추가로 입력해주세용")
            return
        await self.bot.send_typing(ctx.message.channel)
        searchText = " ".join([arg for arg in args])
        searchText = urllib.parse.quote(searchText)
        youtubeUrl = "https://www.youtube.com/results?search_query={}".format(searchText)

        http = HTTPHandler()
        response = http.get(youtubeUrl, self.headers)
        html = BeautifulSoup(response.read().decode(), 'html.parser')
        _videos = html.find_all("div", {"class": "yt-lockup-content"})
        videos = []
        for video in _videos:
            url = video.find('a').get("href")
            if not "user" in url and not "list" in url:
                videos.append(self.parseVideo(video))
        if videos:
            session = Session()
            session.set(videos)
            video = session.first()
            description = self.videoDesc(video, session)
            msg = await self.bot.send_message(ctx.message.channel, description)

            emojiMenu = ["⬅", "▶", "➡", "❌"]
            for emoji in emojiMenu:
                await self.bot.add_reaction(msg, emoji)

            while True:
                res = await self.bot.wait_for_reaction(emojiMenu, timeout=30, user=ctx.message.author, message=msg)
                if not res:
                    for emoji in emojiMenu:
                        await self.bot.remove_reaction(msg, emoji, self.bot.user)
                        await self.bot.remove_reaction(msg, emoji, ctx.message.author)
                    return
                elif res.reaction.emoji == "⬅":
                    video = session.prev()
                    description = self.videoDesc(video, session)
                    await self.bot.edit_message(msg, description)
                    await self.bot.remove_reaction(msg, "⬅", ctx.message.author)
                elif res.reaction.emoji == "➡":
                    video = session.next()
                    description = self.videoDesc(video, session)
                    await self.bot.edit_message(msg, description)
                    await self.bot.remove_reaction(msg, "➡", ctx.message.author)
                elif res.reaction.emoji == "▶":
                    video = session.current()
                    await self.bot.send_typing(ctx.message.channel)
                    await self.bot.delete_message(msg)
                    await self.bot.delete_message(ctx.message)
                    if await Sound.instance.play(ctx, MusicPlayer.YOUTUBE, video.url):
                        await self.bot.send_message(ctx.message.channel, "**{}**을(를) 재생해용 `{}`".format(video.title, video.time))
                    return
                elif res.reaction.emoji == "❌":
                    await self.bot.delete_message(msg)
                    await self.bot.delete_message(ctx.message)
                    return
        else:
            await self.bot.say("검색 결과가 없어용")

    def videoDesc(self, video, session):
        return "{} `{}/{}`".format(video.url, session.index() + 1, session.count())
    
    def parseVideo(self, video):
        time = video.find("span").string.lstrip("- 길이: ")
        tag = video.find('a')
        return Video(tag.get("title"), "https://www.youtube.com{}".format(tag.get("href")), time)

class Video:
    def __init__(self, title, url, time):
        self.title = title
        self.url = url
        self.time = time

def setup(bot):
    cog = Google(bot)
    bot.add_cog(cog)