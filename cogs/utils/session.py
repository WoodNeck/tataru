class Session:
    def __init__(self):
        self._index = 0
        self._pages = None

    def set(self, pages):
        self._pages = pages
    
    def first(self):
        self._index = 0
        return self._pages[self._index]

    def prev(self):
        if self._index > 0:
            self._index -= 1
        else:
            self._index = len(self._pages) - 1
        return self._pages[self._index]
    
    def next(self):
        if self._index < len(self._pages) - 1:
            self._index += 1
        else:
            self._index = 0
        return self._pages[self._index]
    
    def current(self):
        return self._pages[self._index]

    def index(self):
        return self._index
    
    def count(self):
        return len(self._pages)