import discord
import os
from os import walk
from random import randint
from random import choice
from discord.ext import commands
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
        if not os.path.isdir("{}/{}".format(self.IMAGE_PATH, category)):
            return

        imageName = " ".join(parsedMsg[1:])
        if not imageName:
            return
        if imageName == "목록":
            await self.printJjalList(message.channel, category)
            return
        if imageName == "랜덤":
            await self.deployRandomImage(message.channel, category)
            return

        for image in os.listdir("{}/{}".format(self.IMAGE_PATH, category)):
            if imageName == image.split('.')[0]:
                await self.deployImage(message.channel, category, image)
                return

    async def deployImage(self, channel, category, image):
        with open("{}/{}/{}".format(self.IMAGE_PATH, category, image), "rb") as f:
            await self.bot.send_file(channel, f)
    
    async def deployRandomImage(self, channel, category):
        imageList = os.listdir("{}/{}".format(self.IMAGE_PATH, category))
        image = choice(imageList)
        with open("{}/{}/{}".format(self.IMAGE_PATH, category, image), "rb") as f:
            await self.bot.send_file(channel, f)
    
    async def printJjalList(self, channel, category):
        imageList = os.listdir("{}/{}".format(self.IMAGE_PATH, category))
        imageList = ["🔹" + image.split(".")[0] for image in imageList]
        await self.bot.send_message(channel, "```{}```".format(" ".join(imageList)))

def setup(bot):
    cog = Jjal(bot)
    bot.add_cog(cog)
