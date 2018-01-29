class Music:
    def __init__(self, fileType, fileDir, name, user, length=None):
        self.type = fileType
        self.dir = fileDir
        self.name = name
        self.user = user
        self.length = length