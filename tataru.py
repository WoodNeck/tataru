import os
import discord
import logging
from discord.ext import commands
from cogs.utils.observer import Observer
from constants import DEV_GITHUB_URL


class Tataru(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = kwargs["command_prefix"]
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

    @staticmethod
    def instance(prefix, description):
        bot = Tataru(command_prefix=prefix, description=description)

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
            if not os.path.exists("./data/mutable/{}".format(server.id)):
                serverFolders = ["default", "sound"]
                for folder in serverFolders:
                    os.makedirs("./data/mutable/{}/{}".format(server.id, folder))
                await bot.send_message(defaultChannel, "안뇽하세용 타타루에용!\n명령어는 {} 를 참조해주세용!".format(DEV_GITHUB_URL))
            else:
                await bot.send_message(defaultChannel, "안뇽하세용 타타루에용!\n다시 초대해주셔서 고마워용!\n명령어는 {} 를 참조해주세용!".format(DEV_GITHUB_URL))

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
                await bot.send_message(channel, "지금은 할 수가 없어용. "
                                                "{:.1f}초 뒤에 다시 해주세용!"
                                                "".format(error.retry_after))
        return bot

    def load_cogs(self):
        extensions = []
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and not file.startswith("__init__"):
                extensions.append(file.split('.')[0])
        failed = []
        for extension in extensions:
            try:
                self.load_extension("cogs.{}".format(extension))
            except Exception as e:
                print("{}: {}".format(e.__class__.__name__, str(e)))
                failed.append(extension)
        if failed:
            print("\n{}를 로드하는데 실패했어용.\n".format(" ".join(failed)))
