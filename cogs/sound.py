import discord
import asyncio
import os
import json
import urllib
from discord import opus
from discord.ext import commands
from cogs.utils.botconfig import BotConfig
from cogs.utils.music_player import MusicPlayer
from cogs.utils.http_handler import HTTPHandler

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
    raise RuntimeError("OPUS 라이브러리를 로드하는데 실패했어용. 이것들을 시도해봤어용: {}".format(", ".join(opus_libs)))

class Sound:
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.musicPlayers = dict()
        self.youtubeKey = None
        self.SOUND_PATH = "./data/mutable/sound"
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

    async def leaveVoice(self, server):
        voiceClient = self.bot.voice_client_in(server)
        if voiceClient:
            voiceChannel = voiceClient.channel
            await voiceClient.disconnect()
        player = self.musicPlayers.get(server.id)
        if player:
            self.musicPlayers.pop(server.id)

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
        soundString = " ".join([arg for arg in args])
        if soundString == "목록":
            await self.printSoundList(ctx)      
        else:        
            soundPath = "{}/{}.mp3".format(self.SOUND_PATH, soundString) # Only .mp3 file is allowed
            if os.path.exists(soundPath):
                await self.play(ctx, MusicPlayer.LOCAL, soundPath)
            else:
                await self.bot.say("없는 사운드에용")
    
    @commands.command(pass_context=True)
    async def 유튜브(self, ctx, *args):
        if len(args) == 0:
            await self.bot.say("검색어를 추가로 입력해주세용")
            return
        search = " ".join([arg for arg in args])
        search = urllib.parse.quote(search)
        youtubeUrl = "https://www.googleapis.com/youtube/v3/search" \
                    "?part=snippet" \
                    "&key={}" \
                    "&order=viewCount" \
                    "&q={}" \
                    "&maxResults=10" \
                    "&type=video".format(self.youtubeKey, search)

        http = HTTPHandler()
        response = http.get(youtubeUrl, None)
        rescode = response.getcode()
        if (rescode==200):
            response_body = response.read()
            response_body = json.loads(response_body)
            print(response_body)
            result = []
            items = response_body["items"]
            cnt = 1
            for item in items:
                result.append("`{}` {}({}) `{}`".format(cnt, item["snippet"]["title"], "https://youtu.be/{}".format(item["id"]["videoId"]), item["snippet"]["channelTitle"]))
                cnt += 1
            await self.bot.send_message(ctx.message.channel, "\n".join(result))
        else:
            await self.bot.say("오류가 발생했어용\n{}".format(response.read()))
        
        #await self.play(ctx, MusicPlayer.YOUTUBE, youtubeUrl)

    async def play(self, ctx, dataType, song):
        voiceClient = await self.joinVoice(ctx)
        if voiceClient is not None:
            musicPlayer = self.musicPlayers.get(ctx.message.server.id)
            if not musicPlayer:
                musicPlayer = MusicPlayer(self, voiceClient, ctx.message.server, ctx.message.channel)
                self.musicPlayers[ctx.message.server.id] = musicPlayer
            data = (dataType, song)
            musicPlayer.add(data)
            await musicPlayer.play()
    
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
    
    async def printSoundList(self, ctx):
        soundList = []
        for (dirpath, dirnames, filenames) in os.walk("./data/sound"):
            soundList.extend(filenames)
            break
        soundList = ["🎶{}".format(sound.split(".")[0]) for sound in soundList]
        desc = "\n".join(soundList)
        await self.bot.send_message(ctx.message.channel, "```재생가능한 음성 목록이에용\n{}```".format(desc))

def setup(bot):
    cog = Sound(bot)
    config = BotConfig()
    cog.youtubeKey = config.request("Youtube", "API_KEY")
    config.save()
    bot.add_cog(cog)
