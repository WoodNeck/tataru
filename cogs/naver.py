import discord
import os
import json
import urllib
import requests
from discord.ext import commands
from cogs.utils.botconfig import BotConfig
from cogs.utils.observable import Observable
from cogs.utils.http_handler import HTTPHandler
from cogs.utils.html_stripper import HTMLStripper

class Naver(Observable):
    def __init__(self, bot):
        self.bot = bot
        self.naverClient = dict()
        self.bot.listenPublicMsg(self)
    
    def setNaverClient(self, clientId, clientSecret):
        self.naverClient["X-Naver-Client-Id"] = clientId
        self.naverClient["X-Naver-Client-Secret"] = clientSecret

    @commands.command(pass_context=True)
    async def 지식인(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("검색할 내용을 추가로 입력해주세용")
            return
        self.bot.send_typing(ctx.message.channel)
        search = "".join([arg for arg in args])
        encText = urllib.parse.quote(search.encode("utf-8"))
        url = "https://openapi.naver.com/v1/search/kin.json?query={}".format(encText)

        http = HTTPHandler()
        response = http.get(url, self.naverClient)
        rescode = response.getcode()
        if (rescode==200):
            response_body = response.read().decode()
            response_body = json.loads(response_body)
            items = response_body["items"]
            title = "{}에 대한 지식인 검색 결과에용".format(search)
            em = discord.Embed(title=title, colour=0xDEADBF)
            cnt = 0
            for item in items:
                cnt += 1
                stripper = HTMLStripper()
                em.add_field(name=stripper.strip_tags(item["title"]), value=stripper.strip_tags(item["description"]))
                if cnt == 5:
                    break
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode("utf-8")))
    
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

        http = HTTPHandler()
        response = http.post(url, self.naverClient, data)
        rescode = response.getcode()
        if(rescode==200):
            response_body = response.read().decode("utf-8")
            response_body = json.loads(response_body)
            em = discord.Embed(description="{} {}".format(translateFlag[lang], response_body["message"]["result"]["translatedText"]), colour=0xDEADBF)
            await self.bot.send_message(channel, embed=em)
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode("utf-8")))

    @commands.command(pass_context=True)
    async def 로마자변환(self, ctx, args):
        if len(args) <= 10:
            self.bot.send_typing(ctx.message.channel)
            encText = urllib.parse.quote(args)
            url = "https://openapi.naver.com/v1/krdict/romanization?query=" + encText

            http = HTTPHandler()
            response = http.get(url, self.naverClient)
            rescode = response.getcode()
            if (rescode==200):
                response_body = response.read().decode("utf-8")
                response_body = json.loads(response_body)
                if len(response_body["aResult"]):
                    em = discord.Embed(description=response_body["aResult"][0]["aItems"][0]["name"], colour=0xDEADBF)
                    await self.bot.send_message(ctx.message.channel, embed=em)
                else:
                    await self.bot.say("해당 이름에 대한 로마자변환에 실패했어용")
            else:
                await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode("utf-8")))
        else:
            await self.bot.say("10자 이하의 이름을 입력해주세용")

    @commands.command(pass_context=True)
    async def 얼굴인식(self, ctx, args):
        EMOTION = dict()
        EMOTION["angry"] = "화난"
        EMOTION["disgust"] = "혐오감을 느끼는"
        EMOTION["fear"] = "공포를 느끼는"
        EMOTION["laugh"] = "웃고 있는"
        EMOTION["neutral"] = "무표정인"
        EMOTION["sad"] = "슬픈"
        EMOTION["surprised"] = "놀란"
        EMOTION["smile"] = "미소짓고 있는"
        EMOTION["talking"] = "말하고 있는"
        GENDER = {"male": "남자", "female": "여자"}

        self.bot.send_typing(ctx.message.channel)
        tempDir = os.path.join(os.path.split(os.path.dirname(__file__))[0], "temp", "faceRecog.png")

        url_face = "https://openapi.naver.com/v1/vision/face"
        url_celebrity = "https://openapi.naver.com/v1/vision/celebrity"
        
        f = open(tempDir,"wb")
        http = HTTPHandler()
        image_url = args
        image = http.get(image_url, headers={"User-Agent": "Mozilla/5.0"})
        f.write(image.read())
        f.close()

        file = {"image": open(tempDir, "rb")}
        response_face = requests.post(url_face, files=file, headers=self.naverClient)
        rescode_face = response_face.status_code
        response_face = json.loads(response_face.text)

        file = {"image": open(tempDir, "rb")}
        response_celebrity = requests.post(url_celebrity, files=file, headers=self.naverClient)
        rescode_celebrity = response_celebrity.status_code
        response_celebrity = json.loads(response_celebrity.text)

        if(rescode_celebrity == 200 and rescode_face == 200):
            em = discord.Embed(title="얼굴인식 결과에용", colour=0xDEADBF)
            em.set_image(url=args)
            if response_celebrity["info"]["faceCount"]:
                celebrity = response_celebrity["faces"][0]["celebrity"]
                em.add_field(name="닮은꼴 연예인", value="**{}**을(를) 닮았어용!({:.1f}%)".format(celebrity["value"], 100*celebrity["confidence"]))
            if response_face["info"]["faceCount"]:
                age = response_face["faces"][0]["age"]
                em.add_field(name="나이", value="**{}**살 같아용!({:.1f}%)".format(age["value"], 100*age["confidence"]))
                gender = response_face["faces"][0]["gender"]
                em.add_field(name="성별", value="**{}**인 것 같아용!({:.1f}%)".format(GENDER[gender["value"]], 100*gender["confidence"]))
                emotion = response_face["faces"][0]["emotion"]
                em.add_field(name="감정", value="**{}** 것 같아용!({:.1f}%)".format(EMOTION[emotion["value"]], 100*emotion["confidence"]))

            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            if (rescode_face != 200):
                await self.bot.say("얼굴인식에 실패했어용: {}".format(response_face["errorMessage"]))
            elif (rescode_celebrity != 200):
                await self.bot.say("얼굴인식에 실패했어용: {}".format(response_celebrity["errorMessage"]))
        
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def 네이버이미지(self, ctx, *args):
        self.bot.send_typing(ctx.message.channel)
        searchText = " ".join([arg for arg in args])
        encText = urllib.parse.quote(searchText)
        url = "https://openapi.naver.com/v1/search/image?query=" + encText

        http = HTTPHandler()
        response = http.get(url, self.naverClient)
        rescode = response.getcode()
        if (rescode==200):
            response_body = response.read().decode("utf-8")
            response_body = json.loads(response_body)
            if response_body["total"]:
                picture = response_body["items"][0]
                em = discord.Embed(title=picture["title"], colour=0xDEADBF)
                em.set_image(url=picture["link"])
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.say("검색결과가 없어용")
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode("utf-8")))

def setup(bot):
    naver = Naver(bot)
    config = BotConfig()
    clientId = config.request("Naver", "Client_ID")
    clientSecret = config.request("Naver", "Client_Secret")
    naver.setNaverClient(clientId, clientSecret)
    config.save()
    bot.add_cog(naver)