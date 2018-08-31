import urllib
from discord import Embed
from urllib.error import URLError
from discord.ext import commands
from bs4 import BeautifulSoup
from cogs.utils.session import Session, Page
from cogs.utils.http_handler import HTTPHandler


class Games:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def 메타(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("검색할 내용을 추가로 입력해주세용")
            return
        await self.bot.send_typing(ctx.message.channel)
        searchText = " ".join([arg for arg in args])
        encText = urllib.parse.quote(searchText.encode("utf-8"))
        baseUrl = "http://www.metacritic.com"
        searchUrl = "{}/search/all/{}/results".format(baseUrl, encText)
        headers = {}
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        http = HTTPHandler()
        try:
            response = http.get(searchUrl, headers)
        except URLError:
            await self.bot.say("문서가 존재하지 않아용")
            return

        html = BeautifulSoup(response.read().decode(), "html.parser")
        results = html.find("ul", {"class": "search_results"})

        if not results:
            recommendTag = html.find("div", {"class": "search_results"}).find('a')
            if recommendTag:
                recommendation = recommendTag.get_text()
                await self.bot.say("검색결과가 존재하지 않아용, 혹시 **{}**을(를) 검색하려던거 아닌가용?".format(recommendation))
            else:
                await self.bot.say("검색결과가 존재하지 않아용")
        else:
            results = results.find_all("li")
            pages = list()
            for result in results:
                stats = result.find("div", {"class": "main_stats"})
                score = stats.find("span", {"class": "metascore_w"})
                if score is None:
                    continue
                score = score.get_text()
                title = stats.find("h3", {"class": "product_title"}).get_text().strip()
                url = stats.find("h3", {"class": "product_title"}).find('a')['href']
                url = "{}{}".format(baseUrl, url)
                genre = stats.find("p").get_text().strip()
                desc = result.find("p", {"class": "basic_stat"})
                if desc:
                    desc = desc.get_text()
                if genre.count('\n'):
                    genres = genre.split('\n')
                    platform = genres[0]
                    type_year = genres[2].strip().split(',')
                    genre = "{}[{}]".format(type_year[0], platform)
                    year = type_year[1].lstrip()
                else:
                    year = genre.split(',')[1].lstrip()
                    genre = genre.split(',')[0]
                    
                thumb = result.find("img")['src']
                try:
                    score = int(score)
                    if score > 60:
                        color = 0x66cc33
                    elif score > 40:
                        color = 0xffcc33
                    else:
                        color = 0xff0000
                except ValueError:
                    color = Embed.Empty

                page = Page(title=title, desc=desc, url=url, thumb=thumb, color=color)
                page.add_field('score', "**{}**".format(score))
                page.add_field('genre', genre)
                page.add_field('year', year)
                pages.append(page)

            if (len(pages) == 0):
                await self.bot.say("점수가 붙은 항목이 하나도 없는 것 같아용")
                return

            session = Session(self.bot, ctx.message, pages, show_footer=True)
            await session.start()

def setup(bot):
    cog = Games(bot)
    bot.add_cog(cog)