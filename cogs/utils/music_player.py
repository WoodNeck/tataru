import asyncio
import os
from queue import Queue

class MusicPlayer:
    NULL = 0
    LOCAL = 1
    YOUTUBE = 2
    TTS = 3

    def __init__(self, cog, voiceClient, server, channel):
        self.queue = Queue()
        self.cog = cog
        self.voiceClient = voiceClient
        self.server = server
        self.channel = channel
        self.player = None
        self.currentType = MusicPlayer.NULL
        self.currentSong = None
    
    def makeLocalPlayer(self, song):
        self.player = self.voiceClient.create_ffmpeg_player(song, after=self.afterPlay)
    
    async def makeYoutubePlayer(self, url):
        self.player = await self.voiceClient.create_ytdl_player(url, after=self.afterPlay)

    def add(self, song):
        self.queue.put(song)
    
    async def play(self):
        if not self.shouldPlay():
            return
        if not self.queue.empty():
            (self.currentType, self.currentSong) = self.queue.get_nowait()
            if self.currentType == MusicPlayer.LOCAL or self.currentType == MusicPlayer.TTS:
                self.makeLocalPlayer(self.currentSong)
            elif self.currentType == MusicPlayer.YOUTUBE:
                await self.makeYoutubePlayer(self.currentSong)
            else:
                print("MusicPlayer 재생시 dataType값이 범위 외: {}".format(self.currentType))
            self.player.start()
        else:
            await self.cog.leaveVoice(self.server)
    
    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None
            if self.currentType == MusicPlayer.TTS:
                os.remove(self.currentSong)
            self.currentSong = None
            self.currentType = MusicPlayer.NULL

    async def skip(self):
        self.stop()
        await self.play()
    
    def afterPlay(self):
        asyncio.run_coroutine_threadsafe(self.skip(), self.cog.loop)

    def shouldPlay(self):
        if not self.player:
            return True
        if not self.player.is_playing():
            return True
        return False