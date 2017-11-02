import os
import sys
import logging
import discord
from cogs.utils.observer import Observer
from cogs.utils.botconfig import BotConfig
from discord.ext import commands

des = "타타루에용"
prefix = "타타루 "
config = "./config.ini"

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=prefix, **kwargs)
        self.prefix = prefix
        self.privateMsgObserver = Observer()
        self.publicMsgObserver = Observer()
    
    def listenPrivateMsg(self, observable):
        self.privateMsgObserver.register(observable)
        print("{}을 private message listener에 추가했어용".format(observable))
    
    def listenPublicMsg(self, observable):
        self.publicMsgObserver.register(observable)
        print("{}을 public message listener에 추가했어용".format(observable))
    
    def dropPrivateMsg(self, observable):
        self.privateMsgObserver.unregister(observable)
        print("{}을 private message listener에서 제거했어용".format(observable))

    def dropPublicMsg(self, observable):
        self.publicMsgObserver.unregister(observable)
        print("{}을 public message listener에서 제거했어용".format(observable))
    
    async def updatePrivate(self, message):
        await self.privateMsgObserver.update(message)

    async def updatePublic(self, message):
        await self.publicMsgObserver.update(message)

def initialize(bot_class=Bot):
    bot = bot_class(description=des)

    @bot.event
    async def on_ready():
        print("{}".format(discord.version_info))
        print("{} 준비 다됬어용".format(bot.user))
        await bot.change_presence(game=discord.Game(name="{}".format(prefix)))

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)

        if ctx.command is None:
            return

        async with ctx.acquire():
            await self.invoke(ctx)

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        if (message.channel.type == discord.ChannelType.private):
            await bot.updatePrivate(message)
        else:
            await bot.updatePublic(message)
        await bot.process_commands(message)

    @bot.event
    async def on_command_error(error, ctx):
        channel = ctx.message.channel
        if isinstance(error, commands.MissingRequiredArgument):
            await bot.send_message(channel, "명령어 인자가 부족해용")
        elif isinstance(error, commands.BadArgument):
            await bot.send_message(channel, "명령어 인자가 잘못되었어용.")
        elif isinstance(error, commands.DisabledCommand):
            await bot.send_message(channel, "비활성화된 명령어에용.")
        elif isinstance(error, commands.CommandInvokeError):
            await bot.send_message(channel, str(error))
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            await bot.send_message(channel, "명령어 실행에 실패했어용: {}".format(error))
        elif isinstance(error, commands.NoPrivateMessage):
            pass
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.send_message(channel, "지금은 할 수가 없어용"
                                            "{:.2f}초 뒤에 다시 해주세용"
                                            "".format(error.retry_after))
    return bot

def load_cogs(bot):
    extensions = []
    for file in os.listdir("./cogs"):
        if file.endswith(".py") and not file.startswith("__init__"):
            extensions.append(file.split('.')[0])

    failed = []
    for extension in extensions:
        try:
            bot.load_extension("cogs.{}".format(extension))
        except Exception as e:
            print("{}: {}".format(e.__class__.__name__, str(e)))
            failed.append(extension)

    if failed:
        print("\n{}를 로드하는데 실패했어용.\n".format(" ".join(failed)))

if __name__ == '__main__':
    bot = initialize()
    load_cogs(bot)

    user_token = ""
    config = BotConfig(config)
    token = config.request("BotUser", "Token")
    config.request("Naver", "Client_ID")
    config.request("Naver", "Client_Secret")
    config.save()

    bot.run(token)