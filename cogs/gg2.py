import discord
from discord.ext import commands
from cogs.utils.observable import Observable
from cogs.utils.http_handler import HTTPHandler

class GG2(Observable):
    def __init__(self, bot):
        self.bot = bot
        self.bot.listenPublicMsg(self)

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
    
    @commands.command(pass_context=True)
    async def 갱게로비(self, ctx, *arg):
        GG2_LOBBY_URL = "http://www.ganggarrison.com/lobby/status"
        http = HTTPHandler()
        response = http.get(GG2_LOBBY_URL, None)
        rescode = response.getcode()
        if (rescode==200):
            response_body = response.read().decode()
            serverList = self.findServerList(response_body)
            em = discord.Embed(title="Lobby Status", colour=0xDEADBF)
            for server in serverList:
                personPercentage = server.current / server.max
                if personPercentage < 0.33:
                    personEmoji = "☠️"
                elif personPercentage < 0.66:
                    personEmoji = "🙇"
                else:
                    personEmoji = "🙌"
                desc = "🗺️: {}\n🛠️: {}\n{}: {}/{}".format(server.map, server.mod, personEmoji, server.current, server.max)
                em.add_field(name="💠 {}".format(server.name), value=desc)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read().decode("utf-8")))
    
    def findServerList(self, body):
        serverList = []
        serverTable = body.find("<tbody>")
        if serverTable == -1:
            return
        serverNext = body.find("<tr>", serverTable) + 1

        def findNextCell(body, startIndex):
            return body.find("<td>", startIndex + 1)

        def getCellContent(body, startIndex):
            endIndex = body.find("</td>", startIndex)
            cell = body[startIndex + 4:endIndex]
            return cell

        while (serverNext > 0):
            server = ServerInfo()
            cell = findNextCell(body, serverNext) # Exclude Blank Cell

            cell = findNextCell(body, cell)       # Name
            server.name = getCellContent(body, cell)

            cell = findNextCell(body, cell)       # Map
            server.map = getCellContent(body, cell)

            cell = findNextCell(body, cell)       # PlayerInfo
            playerInfo = getCellContent(body, cell).split("/")
            server.current = int(playerInfo[0])
            server.max = int(playerInfo[1])

            cell = findNextCell(body, cell)       # Mod
            modInfo = getCellContent(body, cell)
            modStart = modInfo.find(">") + 1
            modEnd = modInfo.rfind("</a>")
            server.mod = modInfo[modStart:modEnd]
            serverList.append(server)

            serverNext = body.find("<tr>", serverNext) + 1
        
        return serverList
        
class ServerInfo:
    def __init__(self):
        self.name = None
        self.map = None
        self.mod = None
        self.current = None
        self.max = None

def setup(bot):
    cog = GG2(bot)
    bot.add_cog(cog)