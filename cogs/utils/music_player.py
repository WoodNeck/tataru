import asyncio
import os
from .music_type import MusicType
from .music_queue import MusicQueue

class MusicPlayer:
    def __init__(self, cog, voiceClient, server, channel):
        self.queue = MusicQueue()
        self.cog = cog
        self.voiceClient = voiceClient
        self.server = server
        self.channel = channel
        self.player = None
        self.currentSong = None
    
    def makeLocalPlayer(self, fileDir):
        self.player = self.voiceClient.create_ffmpeg_player(fileDir, after=self.afterPlay)
    
    async def makeYoutubePlayer(self, url):
        self.player = await self.voiceClient.create_ytdl_player(url, after=self.afterPlay)

    def add(self, song):
        self.queue.enqueue(song)
    
    async def play(self):
        if not self.shouldPlay():
            return
        self.currentSong = self.queue.dequeue()
        if self.currentSong is not None:
            if self.currentSong.type == MusicType.LOCAL or self.currentSong.type == MusicType.TTS:
                self.makeLocalPlayer(self.currentSong.dir)
            elif self.currentSong.type == MusicType.YOUTUBE:
                await self.makeYoutubePlayer(self.currentSong.dir)
            else:
                print("MusicPlayer 재생시 dataType값이 범위 외: {}".format(self.currentType))
                return
            songDesc = self.makeSongDesc(self.currentSong)
            await self.cog.bot.send_message(self.channel, songDesc)
            self.player.start()
        else:
            await self.cog.leaveVoice(self.server)
    
    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None
            if self.currentSong.type == MusicType.TTS:
                os.remove(self.currentSong.dir)
            self.currentSong = None

    async def skip(self):
        self.stop()
        await self.play()
    
    def afterPlay(self):
        if self.player.is_done():
            asyncio.run_coroutine_threadsafe(self.skip(), self.cog.loop)
        
    def shouldPlay(self):
        if not self.player:
            return True
        if not self.player.is_playing():
            return True
        return False

    def makeSongDesc(self, song):
        if song.length is not None:
            return "{} **{}**을(를) 재생해용 `[{}]`".format(MusicType.toEmoji(song.type), song.name, song.length)
        else:
            return "{} **{}**을(를) 재생해용".format(MusicType.toEmoji(song.type), song.name)