import os
import asyncio
import logging
from discord import opus, ClientException
from discord.ext import commands
from discord.opus import OpusNotLoaded
from cogs.utils.music import Music
from cogs.utils.music_type import MusicType
from cogs.utils.music_player import MusicPlayer

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


class Sound:
    instance = None

    def __init__(self, bot):
        Sound.instance = self
        self.bot = bot
        self.loop = bot.loop
        self.lock = asyncio.Lock()
        self.musicPlayers = dict()
        self.SOUND_PATH = "./data/mutable"

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
        except asyncio.TimeoutError:
            await self.bot.send_message(ctx.message.channel, "음성 채널에 접속하는데 너무 오래 걸려서 못들어가겠어용")
        except ClientException:  # join_voice_channel이 동시에 호출되어 다른 쪽이 먼저 처리된 경우
            return self.bot.voice_client_in(ctx.message.server)
        except OpusNotLoaded:
            await self.bot.send_message(ctx.message.channel, "Opus 라이브러리가 로드되지 않았어용")
            logging.error("Opus Library Not Loaded")
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "문제가 발생하여 음성 채널에 접속할 수 없어용")
            logging.error(str(e))
        return None

    async def leaveVoice(self, server):
        player = self.musicPlayers.get(server.id)
        if player:
            player.stop()
            self.musicPlayers.pop(server.id)
        voiceClient = self.bot.voice_client_in(server)
        if voiceClient:
            await voiceClient.disconnect()

    @commands.command(pass_context=True)
    async def 들어와(self, ctx):
        await self.joinVoice(ctx)

    @commands.command(pass_context=True)
    async def 나가(self, ctx):
        await self.leaveVoice(ctx.message.server)

    @commands.command(pass_context=True)
    async def 재생해줘(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("재생할 사운드를 추가로 입력해주세용")
            return
        soundName = " ".join([arg for arg in args])
        if soundName == "목록":
            await self.printSoundList(ctx.message)
        else:
            soundPath = "{}/{}/sound/{}.mp3".format(self.SOUND_PATH, ctx.message.server.id, soundName)  # Only .mp3 file is allowed
            if os.path.exists(soundPath):
                await self.play(ctx, MusicType.LOCAL, soundPath, soundName)
            else:
                await self.bot.say("없는 사운드에용")

    async def play(self, ctx, dataType, fileDir, name, length=None):
        await self.lock.acquire()
        voiceClient = await self.joinVoice(ctx)
        if voiceClient is not None:
            await self.bot.send_typing(ctx.message.channel)
            musicPlayer = self.musicPlayers.get(ctx.message.server.id)
            if not musicPlayer:
                musicPlayer = MusicPlayer(self, voiceClient, ctx.message.server, ctx.message.channel)
                self.musicPlayers[ctx.message.server.id] = musicPlayer
            song = Music(dataType, fileDir, name, ctx.message.author, length)
            if musicPlayer.currentSong is not None:
                await self.bot.say("{}을(를) 재생목록에 추가했어용".format(song.desc()))
            musicPlayer.add(song)
            await musicPlayer.play()
        self.lock.release()

    async def addList(self, ctx, dataType, videos):
        await self.lock.acquire()
        voiceClient = await self.joinVoice(ctx)
        if voiceClient is not None:
            await self.bot.send_typing(ctx.message.channel)
            musicPlayer = self.musicPlayers.get(ctx.message.server.id)
            if not musicPlayer:
                musicPlayer = MusicPlayer(self, voiceClient, ctx.message.server, ctx.message.channel)
                self.musicPlayers[ctx.message.server.id] = musicPlayer
            for video in videos:
                song = Music(dataType, video.videoUrl, video.videoTitle, ctx.message.author, video.videoTime)
                musicPlayer.add(song)
            await musicPlayer.play()
            await self.bot.send_message(ctx.message.channel, "{}개의 재생목록을 추가했어용".format(len(videos)))
        self.lock.release()

    @commands.command(pass_context=True)
    async def 정지(self, ctx):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if musicPlayer:
            musicPlayer.stop()
            self.musicPlayers.pop(ctx.message.server.id)

    @commands.command(pass_context=True)
    async def 스킵(self, ctx):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if musicPlayer:
            await musicPlayer.skip()

    @commands.command(pass_context=True)
    async def 취소(self, ctx, index):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if not musicPlayer:
            return
        try:
            index = int(index) - 1
        except ValueError:
            self.bot.say("재생목록의 몇번째인지 숫자를 입력해주세용")
            return
        await musicPlayer.skipIndex(ctx, index)

    async def printSoundList(self, message):
        soundPath = "{}/{}/sound".format(self.SOUND_PATH, message.server.id)
        soundList = os.listdir(soundPath)
        soundList = ["🎶" + sound.split(".")[0] for sound in soundList]
        if soundList:
            await self.bot.send_message(message.channel, "```{}```".format(" ".join(soundList)))
        else:
            await self.bot.send_message(message.channel, "재생할 수 있는 음악이 하나도 없어용")

    @commands.command(pass_context=True)
    async def 재생목록(self, ctx):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if musicPlayer:
            await musicPlayer.printSongList(ctx.message.channel)

    @commands.command(pass_context=True)
    async def 현재곡(self, ctx):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if musicPlayer and musicPlayer.currentSong is not None:
            await musicPlayer.displayCurrentStatus(ctx.message.channel)
        else:
            await self.bot.say("재생중인 곡이 없어용")

    @commands.command(pass_context=True)
    async def 루프(self, ctx):
        musicPlayer = self.musicPlayers.get(ctx.message.server.id)
        if musicPlayer:
            musicPlayer.loop = not musicPlayer.loop
            if musicPlayer.loop:
                await self.bot.say("루프를 설정했어용")
            else:
                await self.bot.say("루프를 해제했어용")


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True
    for opus_lib in opus_libs:
        try:
            opus.load_opus(opus_lib)
            return
        except OSError:
            pass
    raise RuntimeError("OPUS 라이브러리를 로드하는데 실패했어용. 이것들을 시도해봤어용: {}".format(", ".join(opus_libs)))


def setup(bot):
    cog = Sound(bot)
    if not __debug__:
        load_opus_lib()
    bot.add_cog(cog)
