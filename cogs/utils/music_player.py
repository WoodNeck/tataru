import asyncio
from queue import Queue

class MusicPlayer:
    def __init__(self, cog, voiceClient, server, channel):
        self.queue = Queue()
        self.cog = cog
        self.voiceClient = voiceClient
        self.server = server
        self.channel = channel
        self.player = None
    
    def makePlayer(self, song):
        self.player = self.voiceClient.create_ffmpeg_player(song, after=self.skip)

    def add(self, song):
        self.queue.put(song)
    
    def play(self):
        if self.shouldPlay():
            if not self.queue.empty():
                song = self.queue.get_nowait()
                self.makePlayer(song)
                self.player.start()
            else:
                asyncio.run_coroutine_threadsafe(self.cog.leaveVoice(self.server), self.cog.loop)
    
    def stop(self):
        if self.player:
            self.player.stop()
            self.player = None

    def skip(self):
        self.stop()
        self.play()

    def shouldPlay(self):
        if not self.player:
            return True
        if not self.player.is_playing():
            return True
        return False