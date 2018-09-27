import os
from discord.ext import commands
from random import choice
from cogs.utils.observable import Observable


class Jjal(Observable):
    def __init__(self, bot):
        self.bot = bot
        self.bot.listenPublicMsg(self)
        self.IMAGE_PATH = "./data/mutable"

    async def update(self, message):
        await self.checkJjalCategory(message)

    async def checkJjalCategory(self, message):
        if not message.content:
            return
        parsedMsg = message.content.split(' ')
        if self.bot.prefix.startswith(parsedMsg[0]):
            parsedMsg = parsedMsg[1:]
        category = parsedMsg[0].lower()
        if category == "sound":
            return
        if not os.path.isdir("{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category)):
            category = "default"
            imageName = " ".join(parsedMsg[0:])
        else:
            imageName = " ".join(parsedMsg[1:])
        if not imageName:
            return
        if imageName == "목록":
            await self.printJjalList(message, category)
            return
        if imageName == "랜덤":
            await self.deployRandomImage(message, category)
            return

        for image in os.listdir("{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category)):
            if imageName == image.split('.')[0]:
                await self.deployImage(message, category, image)
                return

    async def deployImage(self, message, category, image):
        with open("{}/{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category, image), "rb") as f:
            await self.bot.send_file(message.channel, f)

    async def deployRandomImage(self, message, category):
        imageList = os.listdir("{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category))
        image = choice(imageList)
        with open("{}/{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category, image), "rb") as f:
            await self.bot.send_file(message.channel, f)

    async def printJjalList(self, message, category):
        imageList = os.listdir("{}/{}/{}".format(self.IMAGE_PATH, message.server.id, category))
        imageList = ["🔹" + image.split(".")[0] for image in imageList]
        if imageList:
            await self.bot.send_message(message.channel, "```{}```".format(" ".join(imageList)))
        else:
            await self.bot.send_message(message.channel, "폴더 내에 이미지가 한 장도 없어용")

    @commands.command(pass_context=True)
    async def 폴더목록(self, ctx):
        dirList = os.listdir("{}/{}".format(self.IMAGE_PATH, ctx.message.server.id))
        dirList.remove("sound")
        dirList.remove("default")
        dirList = ["🔹" + directory.split(".")[0] for directory in dirList]
        if dirList:
            await self.bot.send_message(ctx.message.channel, "```{}```".format("\n".join(dirList)))
        else:
            await self.bot.send_message(ctx.message.channel, "폴더가 하나도 추가되지 않았어용. 파일관리 명령어로 폴더를 추가해보세용")


def setup(bot):
    cog = Jjal(bot)
    bot.add_cog(cog)
