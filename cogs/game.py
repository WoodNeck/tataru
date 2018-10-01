import json
import urllib
import asyncio
from html import unescape
from discord import Embed
from random import randrange
from urllib.error import URLError
from discord.ext import commands
from bs4 import BeautifulSoup
from cogs.utils.session import Session, Page
from cogs.utils.http_handler import HTTPHandler
from cogs.utils.markdown import *


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

    @commands.command(pass_context=True)
    async def 퀴즈(self, ctx, *args):
        """타타루 퀴즈 `카테고리` `난이도`
        타타루 퀴즈 `목록`
        """
        category = ["전체", "일반상식", "책", "영화", "음악", "뮤지컬", "텔레비젼", "게임", "보드게임", "자연과학", "컴퓨터", "수학", "신화", "스포츠", "지리", "역사", "정치", "예술", "유명인", "동물", "자동차", "만화", "앱등이", "일뽕", "미애니"]
        difficulty = {"랜덤": "", "쉬움": "easy", "중간": "medium", "어려움": "hard"}
        difficultyColors = {"easy": 0x66cc33, "medium": 0xffcc33, "hard": 0xff0000}
        argc = len(args)

        if argc > 0 and args[0] == "목록":
            categoryStr = " ".join(category)
            difficultyStr = " ".join(difficulty)
            await self.bot.say(block("카테고리\n{}\n\n난이도\n{}".format(categoryStr, difficultyStr), ""))
            return
        if len(args) != 2:
            await self.bot.say("타타루 퀴즈 `카테고리` `난이도`를 말해주세용!")
            return
        selected_category = args[0]
        selected_difficulty = args[1]
        if selected_category not in category:
            categoryStr = " ".join(category)
            await self.bot.say("다음 카테고리 중 하나를 선택해주세용!\n{}".format(block(categoryStr, "")))
            return
        if selected_difficulty not in difficulty:
            difficultyStr = " ".join(difficulty)
            await self.bot.say("다음 난이도 중 하나를 선택해주세용!\n{}".format(block(difficultyStr, "")))
            return
        category_index = category.index(selected_category)
        category_index = 0 if category_index == 0 else category_index + 8
        difficulty_index = difficulty[selected_difficulty]

        url = "https://opentdb.com/api.php?amount=1&category={}&difficulty={}".format(category_index, difficulty_index)
        http = HTTPHandler()
        response = http.get(url, {})
        rescode = response.getcode()
        if rescode != 200:
            await self.bot.say("API 접근에 실패했어용! {}".format(rescode))
            return
        response_body = response.read().decode()
        response_body = json.loads(response_body)
        result = response_body["results"][0]
        question = "[{}]\n❓ {}".format(result["difficulty"].upper(), unescape(result["question"]))
        answerCnt = len(result["incorrect_answers"]) + 1
        correct_index = randrange(0, answerCnt)
        correct_answer = result["correct_answer"]
        answers = result["incorrect_answers"]
        answers.insert(correct_index, correct_answer)
        for i in range(answerCnt):
            answers[i] = unescape(answers[i])

        num_emojis = ["1⃣", "2⃣", "3⃣", "4⃣"]
        desc = []
        for i in range(answerCnt):
            desc.append("{} {}".format(num_emojis[i], answers[i]))
        desc = "\n".join(desc)

        difficulty_color = difficultyColors[result["difficulty"]]
        embed = Embed(title=question, description=desc, colour=difficulty_color)
        embedMsg = await self.bot.send_message(ctx.message.channel, embed=embed)
        for i in range(answerCnt):
            await self.bot.add_reaction(embedMsg, num_emojis[i])
        
        await asyncio.sleep(15)

        answerStr = "정답은 {} {}이에용!".format(num_emojis[correct_index], answers[correct_index])
        answer_embed = Embed(title=answerStr, colour=difficulty_color)
        embedMsg = await self.bot.send_message(ctx.message.channel, embed=answer_embed)


def setup(bot):
    cog = Games(bot)
    bot.add_cog(cog)