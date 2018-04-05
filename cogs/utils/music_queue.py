class MusicQueue:
    def __init__(self):
        self.list = []

    def enqueue(self, obj):
        self.list.append(obj)

    def dequeue(self):
        if (len(self.list) > 0):
            return self.list.pop(0)
        else:
            return None

    def empty(self):
        return len(self.list) <= 0
