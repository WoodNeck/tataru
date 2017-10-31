from abc import ABCMeta, abstractmethod
 
class Observable:
    __metaclass__ = ABCMeta
 
    @abstractmethod
    async def update(self, message):
        pass