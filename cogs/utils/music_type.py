class MusicType:
    LOCAL = 0
    YOUTUBE = 1
    TTS = 2

    @classmethod
    def toEmoji(cls, mType):
        if (mType == MusicType.LOCAL):
            return "🎶"
        elif (mType == MusicType.YOUTUBE):
            return "🎵"
        elif (mType == MusicType.TTS):
            return "🗣"
        else:
            return ""
