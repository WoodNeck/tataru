import discord
import json
import urllib.request
from discord.ext import commands
from cogs.utils.botconfig import BotConfig
from cogs.utils.observable import Observable

class Naver(Observable):
    def __init__(self, bot):
        self.bot = bot
        self.client_id = ""
        self.client_secret = ""
        self.bot.listenPublicMsg(self)

    def requestNaver(self, url, data=None):
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        return response

    @commands.command(pass_context=True)
    async def 지식인(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("검색할 내용을 추가로 입력해주세용 ")
            return
        self.bot.send_typing(ctx.message.channel)
        search = "".join([arg for arg in args])
        encText = urllib.parse.quote(search.encode('utf-8'))
        url = "https://openapi.naver.com/v1/search/kin.json?query={}".format(encText)

        response = self.requestNaver(url)
        rescode = response.getcode()
        if (rescode==200):
            response_body = response.read().decode('utf-8')
            response_body = json.loads(response_body)
            items = response_body["items"]
            item = items[0]
            em = discord.Embed(title=item["title"], description=item["description"], colour=0xDEADBF)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode('utf-8')))
    
    async def update(self, message):
        args = message.content.split()
        data = await self.checkTranslateMessage(args, message.channel)
        if data:
            (lang, url, text) = data
            await self.translate(lang, url, text, message.channel)

    async def checkTranslateMessage(self, args, channel):
        if len(args) < 3:
            return
        if args[0] != self.bot.prefix.strip():
            return

        lang = args[1][:-1]
        method = args[2]
        langGiven = self.checkLang(lang)
        methodGiven = self.checkMethod(method)

        translateAbleLang = ["영어", "중국어", "일본어"]
        mtranslateAbleLang = translateAbleLang[:-1]

        if not langGiven and not methodGiven:
            return
        elif langGiven and not methodGiven:
            await self.bot.send_message(channel, "`번역해줘` 또는 `기계번역해줘`가 가능해용")
            return
        elif not langGiven and methodGiven:
            if method == "번역해줘":
                availableLang = translateAbleLang
            else:
                availableLang = mtranslateAbleLang
            await self.noticeAvailableLanguage(channel, availableLang)
            return
        else:
            if method == "번역해줘":
                availableLang = translateAbleLang
                url = "https://openapi.naver.com/v1/language/translate"
            else:
                availableLang = mtranslateAbleLang
                url = "https://openapi.naver.com/v1/papago/n2mt"
            if lang not in availableLang:
                await self.noticeAvailableLanguage(channel, availableLang)
                return
            text = " ".join([arg for arg in args[3:]])
            if text.strip():
                return (lang, url, text)
            else:
                await self.bot.send_message(channel, "번역할 문장을 말해주세용")
    
    def checkLang(self, lang):
        translateAbleLang = ["영어", "중국어", "일본어"]
        if lang in translateAbleLang:
            return True
        else:
            return False
    
    def checkMethod(self, method):
        availableMethod = ["번역해줘", "기계번역해줘"]
        if method in availableMethod:
            return True
        else:
            return False

    async def noticeAvailableLanguage(self, channel, availableLang):
        availableLang = ["`{}`".format(l) for l in availableLang]
        availableLang = ", ".join(availableLang)
        await self.bot.send_message(channel, "가능한 언어는 {}가 있어용".format(availableLang))

    async def translate(self, lang, url, text, channel):
        self.bot.send_typing(channel)
        translateLangToEn = {"영어": "en", "중국어": "zh-CN", "일본어": "ja"}
        translateFlag = {"영어": '🇺🇸', "중국어": '🇨🇳', "일본어": '🇯🇵'}

        encText = urllib.parse.quote(text)
        data = "source=ko&target={}&text=".format(translateLangToEn[lang]) + encText

        response = self.requestNaver(url, data)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read().decode('utf-8')
            response_body = json.loads(response_body)
            em = discord.Embed(description="{} {}".format(translateFlag[lang], response_body["message"]["result"]["translatedText"]), colour=0xDEADBF)
            await self.bot.send_message(channel, embed=em)
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode('utf-8')))

    @commands.command(pass_context=True)
    async def 로마자변환(self, ctx, args):
        if len(args) <= 10:
            self.bot.send_typing(ctx.message.channel)
            encText = urllib.parse.quote(args)
            url = "https://openapi.naver.com/v1/krdict/romanization?query=" + encText

            response = self.requestNaver(url)
            rescode = response.getcode()
            if (rescode==200):
                response_body = response.read().decode('utf-8')
                response_body = json.loads(response_body)
                if len(response_body["aResult"]):
                    em = discord.Embed(description=response_body["aResult"][0]["aItems"][0]["name"], colour=0xDEADBF)
                    await self.bot.send_message(ctx.message.channel, embed=em)
                else:
                    await self.bot.say("해당 이름에 대한 로마자변환에 실패했어용")
            else:
                await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode('utf-8')))
        else:
            await self.bot.say("10자 이하의 이름을 입력해주세용")

def setup(bot):
    naver = Naver(bot)
    config = "./config.ini"
    config = BotConfig(config)
    naver.client_id = config.request("Naver", "Client_ID")
    naver.client_secret = config.request("Naver", "Client_Secret")
    config.save()
    bot.add_cog(naver)