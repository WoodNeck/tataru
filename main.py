# -*- coding: utf-8 -*-
import os
import discord
import logging
from cogs.utils.observer import Observer
from cogs.utils.botconfig import BotConfig
from discord.ext import commands

des = "타타루에용"
prefix = "타타루 "


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=prefix, **kwargs)
        self.prefix = prefix
        self.privateMsgObserver = Observer()
        self.publicMsgObserver = Observer()

    def listenPrivateMsg(self, observable):
        self.privateMsgObserver.register(observable)

    def listenPublicMsg(self, observable):
        self.publicMsgObserver.register(observable)

    def dropPrivateMsg(self, observable):
        self.privateMsgObserver.unregister(observable)

    def dropPublicMsg(self, observable):
        self.publicMsgObserver.unregister(observable)

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
        print("{}개의 서버에서".format(len(bot.servers)))
        print("{}명이 사용 중이에용".format(len(set(bot.get_all_members()))))
        await bot.change_presence(game=discord.Game(name="{}".format(prefix)))

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
    async def on_server_join(server):
        for channel in server.channels:
            defaultChannel = channel
            break
        githubUrl = "https://github.com/WoodNeck/tataru"
        if not os.path.exists("./data/mutable/{}".format(server.id)):
            serverFolders = ["default", "sound"]
            for folder in serverFolders:
                os.makedirs("./data/mutable/{}/{}".format(server.id, folder))
            await bot.send_message(defaultChannel, "안뇽하세용 타타루에용!\n명령어는 {} 를 참조해주세용!".format(githubUrl))
        else:
            await bot.send_message(defaultChannel, "안뇽하세용 타타루에용!\n다시 초대해주셔서 고마워용!\n명령어는 {} 를 참조해주세용!".format(githubUrl))

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
            await bot.send_message(channel, "명령어 실행에 실패했어용")
            if ctx.message.server:
                where = "{}({})/{}({})".format(
                    ctx.message.server.name,
                    ctx.message.server.id,
                    ctx.message.channel.name,
                    ctx.message.channel.id
                )
            else:  # Private Channel
                if ctx.message.channel.owner is not None:  # Single user DM
                    where = "DM with {}({})".format(ctx.message.channel.owner.name, ctx.message.channel.owner.id)
                else:
                    where = "Groupchat {}({})".format(ctx.message.channel.name, ctx.message.channel.id)
            logging.error("{}\n    Caused by: {}\n    In: {}".format(error, ctx.message.content, where))
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
    return failed


if __name__ == '__main__':
    # Changing current working directory to use relative directories
    current_file_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_file_dir)

    bot = initialize()
    load_cogs(bot)

    user_token = ""
    config = BotConfig()
    token = config.request("BotUser", "Token")
    config.save()

    logging.basicConfig(filename='./tataru.log', level=logging.ERROR, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p')

    bot.run(token)
