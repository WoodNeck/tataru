import discord
from discord.ext import commands
import json
import datetime
import asyncio
from random import randint
from random import choice
from pathlib import Path
from dateutil.relativedelta import relativedelta

class General():
    def __init__(self, bot):
        self.bot = bot
        self.military = MilitaryInfo()
        self.military.load()

    @commands.command(hidden=True)
    async def 핑(self):
        await self.bot.say("퐁이에용")

    @commands.command(hidden=True)
    async def 파일관리(self):
        await self.bot.say("http://ec2-13-125-72-67.ap-northeast-2.compute.amazonaws.com:8000/")

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
        choices = [c for c in choices]
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
        if arg == "추가해줘":
            await self.addDischargeInfo(ctx)
        else:
            name = arg
            server = self.military.servers.get(ctx.message.server.id)
            if server and name in server:
                person = server[name]
                ipdae = person.getStartDate()
                discharge = person.getDischargeDate()
                now = datetime.datetime.now().date()
                accomplished = now - ipdae
                left = discharge - now
                total = discharge - ipdae
                donePercentage = accomplished.days * 100 / total.days

                percentVisualization = []
                (doneEmoji, yetEmoji) = person.getEmojiSet()
                doneCount = min(int(donePercentage), 100)

                percentVisualization.append(doneEmoji * doneCount)
                percentVisualization.append(yetEmoji * (100 - doneCount))
                percentVisualization = "".join(percentVisualization)
                
                desc = """
                    {}\n입대일: {}\n전역일: {}\n복무한 날: {}일\n남은 날: {}일\n오늘까지 복무율: {:.2f}%
                """.format(percentVisualization, ipdae.strftime("%Y-%m-%d"), discharge.strftime("%Y-%m-%d"), accomplished.days, left.days, donePercentage)

                em = discord.Embed(title="{}{}의 복무정보에용".format(person.getSymbol(), name), description=desc, colour=0xDEADBF)
                await self.bot.send_message(ctx.message.channel, embed=em)
            else:
                await self.bot.say("그 이름은 등록되어있지 않아용")
    
    async def addDischargeInfo(self, ctx):
        name = await self.checkName(ctx)
        if not name:
            await self.bot.say("취소되었어용")
            return
        
        startDate = await self.checkStartDate(ctx)
        if not startDate:
            return
        
        info = await self.checkArmyType(ctx, startDate)
        if not info:
            await self.bot.say("취소되었어용")
            return

        self.military.setData(ctx.message.server.id, name, info)
        em = discord.Embed(title="{}{}을(를) 추가했어용!".format(info.getSymbol(), name), colour=0xDEADBF)
        await self.bot.send_message(ctx.message.channel, embed=em)

    async def checkName(self, ctx):
        await self.bot.say("등록할 이름을 말해주세용")
        msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=15)
        if msg and msg.content:
            name = msg.content
            return name
    
    async def checkStartDate(self, ctx):
        await self.bot.say("입대일자를 YYYY/MM/DD 양식으로 말해주세용")
        msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=30)
        if msg and msg.content:
            try:
                dateinfo = msg.content.split("/")
                dateinfo = [int(i) for i in dateinfo]
                startDate = datetime.date(dateinfo[0], dateinfo[1], dateinfo[2])
                return startDate
            except Exception as e:
                await self.bot.say("올바른 양식(YYYY/MM/DD)이 아닌 것 같아용")
                return
    
    async def checkArmyType(self, ctx, startDate):
        available = ["육군", "공군", "공익"]
        availableFormatted = ["`{}`".format(m) for m in available]
        await self.bot.say("{}중에 어디에 입대했나용?".format(", ".join(availableFormatted)))
        msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=30)
        if msg and msg.content:
            if msg.content in available:
                if msg.content == "육군":
                    info = Military(startDate)
                elif msg.content == "공군":
                    info = Airforce(startDate)
                elif msg.content == "공익":
                    info = PublicService(startDate)
                return info
            else:
                await self.bot.say("셋 중에 하나를 입력해주세용")


    @commands.command(pass_context=True)
    async def 수능(self, ctx):
        dday = datetime.date(2017, 11, 23)
        t = datetime.time(8, 40, 00)
        sunung = datetime.datetime.combine(dday, t)
        now = datetime.datetime.now()
        diff = sunung - now
        desc = """
            {}시간 {}분 {}초 남았어용
        """.format(diff.days * 24 + diff.seconds // 3600, (diff.seconds % 3600) // 60, diff.seconds %  60)

        em = discord.Embed(title="⏰2018학년도 대학수학능력시험까지 D-{}".format(diff.days), description=desc, colour=0xDEADBF)
        await self.bot.send_message(ctx.message.channel, embed=em)

    @commands.command(pass_context=True)
    async def 투표(self, ctx, *args):
        """
            Usage: `타타루` `투표` `질문` `(옵션1)` `(옵션2)` `...`
        """
        args = [arg for arg in args]
        if not len(args):
            self.bot.say("`타타루` `투표` `질문` `(옵션1)` `(옵션2)` `...`순으로 입력해주세용")
            return
        question = args[0]
        options = args[1:]
        if not options:
            options = ["네", "아니오"]
        optionEmojis = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

        desc = []
        desc.append("🤔: {}?".format(question))
        optionCnt = 0
        for option in options:
            desc.append("{}: {}".format(optionEmojis[optionCnt], options[optionCnt]))
            optionCnt += 1
        desc = "\n".join(desc)
        em = discord.Embed(colour=0xDEADBF, description=desc)
        name = ctx.message.author.nick
        if not name:
            name = ctx.message.author.name
        em.set_footer(text="{}이(가) 제안했어용".format(name), icon_url=ctx.message.author.avatar_url)
        msg = await self.bot.send_message(ctx.message.channel, embed=em)

        optionEmojis = optionEmojis[:len(options)]
        for emoji in optionEmojis:
            await self.bot.add_reaction(msg, emoji)
        
        await asyncio.sleep(30)

        msg = await self.bot.get_message(ctx.message.channel, msg.id)

        reactions = {}
        for reaction in msg.reactions:
            reactions[reaction.emoji] = reaction.count
        
        result = discord.Embed(colour=0xDEADBF, title="🤔: {}? 에 대한 투표 결과에용".format(question))
        optionCnt = 0
        for option in options:
            result.add_field(name="{}: {}".format(optionEmojis[optionCnt], options[optionCnt]),
            value="{}표".format(reactions.get(optionEmojis[optionCnt]) - 1))
            optionCnt += 1

        await self.bot.send_message(ctx.message.channel, embed=result)

class MilitaryInfo:
    def __init__(self):
        self.path = "military_info.json"
        self.servers = dict()
    
    def setData(self, serverId, key, value):
        targetServer = self.servers.get(serverId)
        if not targetServer:
            targetServer = dict()
            self.servers[serverId] = targetServer
        targetServer[key] = value
        self.save()

    def load(self):
        file = Path(self.path)
        if not file.is_file():
            return
        with open(self.path) as info:
            encodedDict = json.load(info)
            for serverHash in encodedDict:
                serverInfo = encodedDict[serverHash]
                self.servers[serverHash] = dict()
                server = self.servers[serverHash]
                for name in serverInfo:
                    personInfo = serverInfo[name]
                    encodedDate = personInfo["startDate"]
                    encodedDate = [int(i) for i in encodedDate.split("/")]
                    encodedDate = datetime.date(encodedDate[0], encodedDate[1], encodedDate[2])
                    if personInfo["class"] == "Military":
                        server[name] = Military(encodedDate)
                    elif personInfo["class"] == "Airforce":
                        server[name] = Airforce(encodedDate)
                    elif personInfo["class"] == "PublicService":
                        server[name] = PublicService(encodedDate)

    def save(self):
        f = open(self.path, "w")
        infoToDump = {}
        for serverId in self.servers:
            serverInfo = self.servers[serverId]
            serverDump = {}
            infoToDump[serverId] = serverDump
            for name in serverInfo:
                serverDump[name] = serverInfo[name].encode()
        f.write(json.dumps(infoToDump))
        f.close()

class Military:
    def __init__(self, startDate):
        self.startDate = startDate
    
    def getStartDate(self):
        return self.startDate

    def getDischargeDate(self):
        return self.startDate + relativedelta(months=18, days=-1)

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
