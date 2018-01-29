class MusicQueue:
    def __init__(self):
        self.queue = []
    
    def enqueue(self, obj):
        self.queue.append(obj)
    
    def dequeue(self):
        if (len(self.queue) > 0):
            return self.queue.pop(0)
        else:
            return None
    
    def empty(self):
        return (len(self.queue) <= 0)