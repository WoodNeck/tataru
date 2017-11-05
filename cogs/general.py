import discord
from discord.ext import commands
import json
import datetime
from random import randint
from random import choice
from pathlib import Path
from cogs.utils.observable import Observable
from dateutil.relativedelta import relativedelta

class General(Observable):
    def __init__(self, bot):
        self.bot = bot
        self.bot.listenPublicMsg(self)
        self.military = MilitaryInfo()
        self.military.load()

    async def update(self, message):
        await self.checkGG2Bubble(message)

    async def checkGG2Bubble(self, message):
        content = message.content.lower()
        length = len(content)
        if content in ["센트리", "우버", 'e']:
            with open("./data/gg2/{}.png".format(content), "rb") as f:
                await self.bot.send_file(message.channel, f)
        elif content == 'f':
            taunt = "{}{}".format(content, randint(0, 9))
            with open("./data/gg2/{}.png".format(taunt), "rb") as f:
                await self.bot.send_file(message.channel, f)
        elif 0 < length <= 3:
            if content[0] in ['z', 'c', 'f']:
                if length != 2:
                    return
                if 49 <= ord(content[1]) <= 57:
                    with open("./data/gg2/{}.png".format(content), "rb") as f:
                        await self.bot.send_file(message.channel, f)
            elif content[0] == 'x':
                try:
                    num = int(content[1:])
                    if 0 <= num <= 29:
                        with open("./data/gg2/{}.png".format(content), "rb") as f:
                            await self.bot.send_file(message.channel, f)
                except:
                    return

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
    async def 따귀(self, ctx, arg):
        await self.bot.say("{}의 뺨을 후려갈겼어용".format(arg))

    @commands.command(pass_context=True)
    async def 전역일(self, ctx, arg):
        available = ["육군", "공군", "공익"]

        if arg == "추가해줘":
            await self.bot.say("등록할 이름을 말해주세용")
            msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=15)
            if msg and msg.content:
                name = msg.content
                await self.bot.say("입대일자를 YYYY/MM/DD 양식으로 말해주세용")
                msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=30)
                if msg and msg.content:
                    try:
                        dateinfo = msg.content.split("/")
                        dateinfo = [int(i) for i in dateinfo]
                        startDate = datetime.date(dateinfo[0], dateinfo[1], dateinfo[2])
                        availableFormatted = ["`{}`".format(m) for m in available]
                    except Exception as e:
                        print(e)
                        await self.bot.say("올바른 양식(YYYY/MM/DD)이 아닌 것 같아용")
                        return
                    await self.bot.say("{}중에 어디에 입대했나용?".format(", ".join(availableFormatted)))
                    msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=15)
                    if msg and msg.content:
                        if msg.content in available:
                            if msg.content == "육군":
                                info = Military(startDate)
                            elif msg.content == "공군":
                                info = Airforce(startDate)
                            elif msg.content == "공익":
                                info = PublicService(startDate)
                            self.military.setData(name, info)

                            em = discord.Embed(title="{}{}를 추가했어용!".format(info.getSymbol(), name), colour=0xDEADBF)
                            await self.bot.send_message(ctx.message.channel, embed=em)
                        else:
                            await self.bot.say("셋 중에 하나를 입력해주세용")
                    else:
                        await self.bot.say("취소되었어용")
                else:
                    await self.bot.say("취소되었어용")
            else:
                await self.bot.say("취소되었어용")
        else:
            name = arg
            if name in self.military.data:
                person = self.military.data[name]
                ipdae = person.getStartDate()
                discharge = person.getDischargeDate()
                now = datetime.datetime.now().date()
                accomplished = now - ipdae
                left = discharge - now
                total = discharge - ipdae
                donePercentage = accomplished.days * 100 / total.days

                percentVisualization = ""
                (doneEmoji, yetEmoji) = person.getEmojiSet()
                for i in range(1, 101):
                    if (donePercentage >= i):
                        percentVisualization += doneEmoji
                    else:
                        percentVisualization += yetEmoji
                
                desc = """
                    {}\n입대일: {}\n전역일: {}\n복무한 날: {}일\n남은 날: {}일\n오늘까지 복무율: {:.2f}%
                """.format(percentVisualization, ipdae.strftime("%Y-%m-%d"), discharge.strftime("%Y-%m-%d"), accomplished.days, left.days, donePercentage)

                em = discord.Embed(title="{}{}의 복무정보에용".format(person.getSymbol(), name), description=desc, colour=0xDEADBF)
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.say("그 이름은 등록되어있지 않아용")

    @commands.command(pass_context=True)
    async def 수능(self, ctx):
        dday = datetime.date(2017, 11, 16)
        t = datetime.time(8, 40, 00)
        sunung = datetime.datetime.combine(dday, t)
        now = datetime.datetime.now()
        diff = sunung - now
        desc = """
            {}시간 {}분 {}초 남았어용
        """.format(diff.days * 24 + diff.seconds // 3600, (diff.seconds % 3600) // 60, diff.seconds %  60)

        em = discord.Embed(title="⏰2018학년도 대학수학능력시험까지 D-{}".format(diff.days), description=desc, colour=0xDEADBF)
        await self.bot.send_message(ctx.message.channel, embed=em)

class MilitaryInfo:
    def __init__(self):
        self.path = "military_info.json"
        self.data = None
    
    def setData(self, key, value):
        self.data[key] = value
        self.save()

    def load(self):
        file = Path(self.path)
        if file.is_file():
            with open(self.path) as info:
                try:
                    encodedDict = json.load(info)
                    self.data = dict()
                    for key in encodedDict:
                        personInfo = encodedDict[key]
                        encodedDate = personInfo["startDate"]
                        encodedDate = [int(i) for i in encodedDate.split("/")]
                        encodedDate = datetime.date(encodedDate[0], encodedDate[1], encodedDate[2])
                        if personInfo["class"] == "Military":
                            self.data[key] = Military(encodedDate)
                        elif personInfo["class"] == "Airforce":
                            self.data[key] = Airforce(encodedDate)
                        elif personInfo["class"] == "PublicService":
                            self.data[key] = PublicService(encodedDate)
                except Exception as e:
                    print(e)
                    self.data = dict()

    def save(self):
        f = open(self.path, "w")
        infoToDump = {}
        for key in self.data:
            infoToDump[key] = self.data[key].encode()
        f.write(json.dumps(infoToDump))
        f.close()

class Military:
    def __init__(self, startDate):
        self.startDate = startDate

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def getStartDate(self):
        return self.startDate

    def getDischargeDate(self):
        return self.startDate + relativedelta(months=21, days=-1)

    def getEmojiSet(self):
        return ("💖", "🖤")
    
    def getSymbol(self):
        return "🔫"

    def encode(self):
        return {"class": "Military", "startDate": self.startDate.strftime("%Y/%m/%d")}

class Airforce(Military):
    def getDischargeDate(self):
        return self.startDate + relativedelta(months=24, days=-1)

    def getEmojiSet(self):
        return ("🏇", "🐎")

    def getSymbol(self):
        return "✈️"
    
    def encode(self):
        return {"class": "Airforce", "startDate": self.startDate.strftime("%Y/%m/%d")}

class PublicService(Military):
    def getEmojiSet(self):
        return ("💖", "🖤")

    def encode(self):
        return {"class": "PublicService", "startDate": self.startDate.strftime("%Y/%m/%d")}

def setup(bot):
    general = General(bot)
    bot.add_cog(general)
