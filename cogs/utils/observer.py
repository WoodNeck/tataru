class Observer:
    def __init__(self):
        self.observers = []

    def register(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def unregister(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def clear(self):
        if self.observers:
            del self.observers[:]

    async def update(self, message):
        for observer in self.observers:
            await observer.update(message)
