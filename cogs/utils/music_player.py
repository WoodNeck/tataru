import asyncio
from queue import Queue

class MusicPlayer:
    LOCAL = 0
    YOUTUBE = 1
    def __init__(self, cog, voiceClient, server, channel):
        self.queue = Queue()
        self.cog = cog
        self.voiceClient = voiceClient
        self.server = server
        self.channel = channel
        self.player = None
    
    def makeLocalPlayer(self, song):
        self.player = self.voiceClient.create_ffmpeg_player(song, after=self.afterPlay)
    
    async def makeYoutubePlayer(self, url):
        self.player = await self.voiceClient.create_ytdl_player(url, after=self.afterPlay)

    def add(self, song):
        self.queue.put(song)
    
    async def play(self):
        if self.shouldPlay():
            if not self.queue.empty():
                (dataType, song) = self.queue.get_nowait()
                if dataType == MusicPlayer.LOCAL:
                    self.makeLocalPlayer(song)
                elif dataType == MusicPlayer.YOUTUBE:
                    await self.makeYoutubePlayer(song)
                self.player.start()
            else:
                await self.cog.leaveVoice(self.server)
    
    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None

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