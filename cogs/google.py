import discord
import urllib
from discord.ext import commands
from cogs.utils.http_handler import HTTPHandler

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
        url = "https://www.google.co.kr/search?q={}&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg".format(encText)
        html = self.getHtml(url)
        images = self.findAllImages(html)
        if not images:
            self.bot.say("검색 결과가 없어용")
            return
        session = ImageSession()
        session.set(images)
        image = session.first()
        
        em = discord.Embed(colour=0xDEADBF)
        em.set_image(url=image)
        em.set_footer(text="{}/{}".format(session.current(), session.count()))
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
                em.set_footer(text="{}/{}".format(session.current(), session.count()))
                await self.bot.edit_message(msg, embed=em)
                await self.bot.remove_reaction(msg, "⬅", ctx.message.author)
            elif res.reaction.emoji == "➡":
                image = session.next()
                em.set_image(url=image)
                em.set_footer(text="{}/{}".format(session.current(), session.count()))
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
                items.append(item)
                page = page[end_content:]
        return items

class ImageSession:
    def __init__(self):
        self.index = 0
        self.pages = None

    def set(self, pages):
        self.pages = pages
    
    def first(self):
        self.index = 0
        return self.pages[self.index]

    def prev(self):
        if self.index > 0:
            self.index -= 1
        else:
            self.index = len(self.pages) - 1
        return self.pages[self.index]
    
    def next(self):
        if self.index < len(self.pages) - 1:
            self.index += 1
        else:
            self.index = 0
        return self.pages[self.index]
    
    def current(self):
        return self.index + 1
    
    def count(self):
        return len(self.pages)

def setup(bot):
    cog = Google(bot)
    bot.add_cog(cog)