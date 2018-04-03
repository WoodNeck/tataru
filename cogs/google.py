import discord
import urllib
import json
from functools import partialmethod
from discord.ext import commands
from .sound import Sound
from cogs.utils.session import Session, Page
from cogs.utils.botconfig import BotConfig
from cogs.utils.music_type import MusicType
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
        self.youtube_key = None

    @commands.command(pass_context=True)
    async def 이미지(self, ctx, *args):
        await self.bot.send_typing(ctx.message.channel)
        if len(args) == 0:
            await self.bot.say("검색어를 추가로 입력해주세용")
            return
        searchText = " ".join([arg for arg in args])
        encText = urllib.parse.quote(searchText.encode('utf-8'))
        url = "https://www.google.co.kr/search?q={}&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg".format(encText)
        html = self.getHtml(url)
        images = self.findAllImages(html)
        if not images:
            self.bot.say("검색 결과가 없어용")
            return
        pages = [Page(image=image) for image in images]
        session = Session(self.bot, ctx.message, pages, show_footer=True)
        await session.start()

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

        if args[0] == "재생해줘":
            if len(args) == 1:
                await self.bot.say("주소를 추가로 입력해주세용")
                return
            searchText = " ".join(args[1:])
            if "list=" in searchText:
                playListId = searchText[searchText.find("list=")+5:].rstrip("&")
                url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={}&key={}".format(playListId, self.youtube_key)
                http = HTTPHandler()
                try:
                    response = http.get(url, None)
                except:
                    self.bot.say("주소가 올바르지 않아용")
                    return
                response_body = json.loads(response.read().decode())
                _videos = response_body.get("items")
                if not _videos:
                    await self.bot.say("주소가 올바르지 않아용")
                    return
                videos = []
                for video in _videos:
                    videos.append((video["snippet"]["title"], "https://youtu.be/{}".format(video["snippet"]["resourceId"]["videoId"])))
                await Sound.instance.addList(ctx, MusicType.YOUTUBE, videos)
            else:
                videos = self.searchVideos(searchText)
                if not videos:
                    await self.bot.say("주소가 올바르지 않아용")
                    return
                video = videos[0]
                await self.bot.delete_message(ctx.message)
                await Sound.instance.play(ctx, MusicType.YOUTUBE, video.url, video.title, video.time)
        else:
            await self.bot.send_typing(ctx.message.channel)
            searchText = " ".join([arg for arg in args])
            videos = self.searchVideos(searchText)
            if not videos:
                await self.bot.say("검색 결과가 없어용")
                return
            session = Session(self.bot, ctx.message, pages, show_footer=True)
            playBtnCallback = partialmethod(self.playVideo, session)
            session.addEmoji("▶", callback=playBtnCallback , pos=1)
            await session.start()

    def searchVideos(self, searchText):
        searchText = urllib.parse.quote(searchText)
        youtubeUrl = "https://www.youtube.com/results?search_query={}".format(searchText)

        http = HTTPHandler()
        response = http.get(youtubeUrl, self.headers)
        html = BeautifulSoup(response.read().decode(), 'html.parser')
        _videos = html.find_all("div", {"class": "yt-lockup-content"})
        videos = []
        for video in _videos:
            url = video.find('a').get("href")
            if not "user" in url and not "list" in url and not "channel" in url and not "googleads" in url:
                videos.append(self.parseVideo(video))
        return videos

    def parseVideo(self, video):
        videoDesc = "{} `[{}]`".format(video.url, video.time)
        videoTitle = video.find('a').get("title")
        videoUrl = "https://www.youtube.com{}".format(video.find('a').get("href"))
        videoTime = video.find("span").string.lstrip("- 길이: ")
        return Video(desc=videoDesc, url=videoUrl, video_time=videoTitle, video_time=time)
    
    def videoDesc(self, video):
        return "{} `[{}]`".format(video.url, video.time)

    async def playVideo(self, session):
        video = session.current()
        await session.deleteMsg()
        await Sound.instance.play(ctx, MusicType.YOUTUBE, video.url, video.videoTitle, video.time)

class Video(Page):
    def __init__(self, title=None, desc=None, url=None, image=None, thumb=None, footer_format=None, video_title=None, video_time=None):
        super(Video, self).__init__(title, desc, url, image, thumb, footer_format)
        self.videoTitle = video_title
        self.videoTime = video_time

def setup(bot):
    cog = Google(bot)
    config = BotConfig()
    cog.youtube_key = config.request("Youtube", "API_KEY")
    config.save()
    bot.add_cog(cog)
