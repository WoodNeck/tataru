import os
import sys
import logging
import discord
#from cogs.mahjong import Mahjong
#from cogs.dangerous_invite import DangerousInvite
from cogs.utils.botconfig import BotConfig
from discord.ext import commands

des = "타타루에용"
prefix = "타타루 "
config = "./config.ini"

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, command_prefix=prefix, **kwargs)

def initialize(bot_class=Bot):
    bot = bot_class(description=des)

    @bot.event
    async def on_ready():
        print("{}".format(discord.version_info))
        print("{} 준비 다됬어용".format(bot.user))
        await bot.change_presence(game=discord.Game(name="{}".format(prefix)))

    """
    @bot.event
    async def on_resumed():
        bot.counter["session_resumed"] += 1
    
    @bot.event
    async def on_command(command, ctx):
        #bot.counter["processed_commands"] += 1
    """

    @bot.event
    async def on_message(message):
        """
        if Mahjong.instance.isPlaying and message.author == Mahjong.instance.playingUser:
            await Mahjong.instance.gotMessage(message)
        if (message.channel.type == discord.ChannelType.private):
            await DangerousInvite.instance.gotPrivateMessage(message)
        else:
            await DangerousInvite.instance.checkTargetMessage(message)
        if len(message.content) == 2:
            if message.content.startswith("z"):
                if 49 <= ord(message.content[1]) <= 57:
                    with open('./data/gg2/{}.png'.format(message.content), 'rb') as f:
                        await bot.send_file(message.channel, f)
            elif message.content.startswith("x"):
                pass
            elif message.content.startswith("c"):
                pass
        """
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


def main(bot):
    load_cogs(bot)

if __name__ == '__main__':
    bot = initialize()
    main(bot)

    user_token = ""
    config = BotConfig(config)
    token = config.request("BotUser", "Token")
    config.request("Naver", "Client_ID")
    config.request("Naver", "Client_Secret")
    config.save()

    bot.run(token)