from .music_type import MusicType


class Music:
    def __init__(self, fileType, fileDir, name, user, length=None):
        self.type = fileType
        self.dir = fileDir
        self.name = name
        self.user = user
        self.length = length

    def desc(self):
        if self.length is not None:
            return "{} **{}** `[{}]`".format(MusicType.toEmoji(self.type), self.name, self.length)
        else:
            return "{} **{}**".format(MusicType.toEmoji(self.type), self.name)
