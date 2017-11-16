import discord
import os
import functools
from discord.ext import commands
from discord import opus

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass

    raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

class SoundPlayer:
    instance = None

    def __init__(self, bot):
        self.bot = bot
        SoundPlayer.instance = self
        self.joinedServer = dict()
        load_opus_lib()

    async def joinVoice(self, ctx):
        try:
            voiceClient = self.bot.voice_client_in(ctx.message.server)
            voiceChannel = ctx.message.author.voice.voice_channel
            if voiceClient is None:
                return await self.bot.join_voice_channel(voiceChannel)
            else:
                if voiceClient.channel != voiceChannel:
                    await voiceClient.move_to(voiceChannel)
                return voiceClient
        except Exception as e:
            print(e)
            await self.bot.send_message(ctx.message.channel, "먼저 보이스채널에 들어가주세용")
            return None

    async def leaveVoice(self, ctx):
        voiceClient = self.bot.voice_client_in(ctx.message.server)
        if voiceClient is not None:
            voiceChannel = voiceClient.channel
            await voiceClient.disconnect()
    
    async def play(self, ctx, soundPath):
        voiceClient = await self.joinVoice(ctx)
        if voiceClient is not None:
            soundPlayer = voiceClient.create_ffmpeg_player(soundPath, after=afterPlay)
            soundPlayer.start()

    @commands.command(pass_context=True)
    async def 들어와(self, ctx):
        await self.joinVoice(ctx)

    @commands.command(pass_context=True)
    async def 나가(self, ctx):
        await self.leaveVoice(ctx)

    @commands.command(pass_context=True)
    async def 재생해줘(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("재생할 사운드를 추가로 입력해주세용")
            return
        soundString = " ".join([arg for arg in args])
        if soundString == "목록":
            soundList = []
            for (dirpath, dirnames, filenames) in os.walk("./data/sound"):
                soundList.extend(filenames)
                break
            soundList = ["🎶{}".format(sound.split(".")[0]) for sound in soundList]
            desc = "\n".join(soundList)
            await self.bot.say("```재생가능한 음성 목록이에용\n{}```".format(desc))
        else:        
            soundPath = "./data/sound/{}.mp3".format(soundString) # Only .mp3 file is allowed
            if os.path.exists(soundPath):
                await self.play(ctx, soundPath)
            else:
                await self.bot.say("없는 사운드에용")
                return

def afterPlay(player):
    player.stop()

def setup(bot):
    cog = SoundPlayer(bot)
    bot.add_cog(cog)
