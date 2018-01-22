import discord
import os
import sys
import json
import urllib
import asyncio
import platform
from discord import opus
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from cogs.utils.session import Session
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
        self.SOUND_PATH = "./data/mutable/sound"
        os.environ["MOZ_HEADLESS"] = '1'
        if platform.system() == "Windows":
            self.fireFoxBinary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        else:
            self.fireFoxBinary = FirefoxBinary()
        
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
        await self.bot.send_typing(ctx.message.channel)
        searchText = " ".join([arg for arg in args])
        searchText = urllib.parse.quote(searchText)
        youtubeUrl = "https://www.youtube.com/results?search_query={}".format(searchText)

        driver = webdriver.Firefox(firefox_binary=self.fireFoxBinary)
        driver.get(youtubeUrl)
        videos = driver.find_elements_by_tag_name("ytd-video-renderer")
        if videos:
            session = Session()
            session.set(videos)
            video = session.first()
            description = self.videoDesc(video, session)
            msg = await self.bot.send_message(ctx.message.channel, description)

            emojiMenu = ["⬅", "▶", "➡", "❌"]
            for emoji in emojiMenu:
                await self.bot.add_reaction(msg, emoji)

            while True:
                res = await self.bot.wait_for_reaction(emojiMenu, timeout=30, user=ctx.message.author, message=msg)
                if not res:
                    for emoji in emojiMenu:
                        await self.bot.remove_reaction(msg, emoji, self.bot.user)
                        await self.bot.remove_reaction(msg, emoji, ctx.message.author)
                    break
                elif res.reaction.emoji == "⬅":
                    video = session.prev()
                    description = self.videoDesc(video, session)
                    await self.bot.edit_message(msg, description)
                    await self.bot.remove_reaction(msg, "⬅", ctx.message.author)
                elif res.reaction.emoji == "➡":
                    video = session.next()
                    description = self.videoDesc(video, session)
                    await self.bot.edit_message(msg, description)
                    await self.bot.remove_reaction(msg, "➡", ctx.message.author)
                elif res.reaction.emoji == "▶":
                    video = session.current()
                    (title, url, time) = self.parseVideo(video)
                    await self.bot.send_typing(ctx.message.channel)
                    await self.bot.delete_message(msg)
                    await self.bot.delete_message(ctx.message)
                    await self.play(ctx, MusicPlayer.YOUTUBE, url)
                    await self.bot.send_message(ctx.message.channel, "**{}**를 재생해용 `{}`".format(title, time))
                    break
                elif res.reaction.emoji == "❌":
                    await self.bot.delete_message(msg)
                    await self.bot.delete_message(ctx.message)
                    break
        else:
            await self.bot.say("검색 결과가 없어용")
        driver.close()
    
    def videoDesc(self, video, session):
        (title, url, time) = self.parseVideo(video)
        return "{} `{}/{}`".format(url, session.index() + 1, session.count())
    
    def parseVideo(self, video):
        time = video.find_element_by_tag_name("ytd-thumbnail-overlay-time-status-renderer").find_element_by_tag_name("span").text
        tag = video.find_element_by_id("video-title")
        return (tag.text, "{}".format(tag.get_attribute("href")), time)

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
        soundList = os.listdir("{}".format(self.SOUND_PATH))
        soundList = ["🎶" + sound.split(".")[0] for sound in soundList]
        await self.bot.send_message(channel, "```{}```".format(" ".join(soundList)))

def setup(bot):
    cog = Sound(bot)
    bot.add_cog(cog)
