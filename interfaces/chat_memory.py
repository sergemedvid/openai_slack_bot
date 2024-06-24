from abc import ABC, abstractmethod

class IChatMemory(ABC):
    @abstractmethod
    def add(self, key, value):
        pass
    
    @abstractmethod
    def format_messages(self):
        pass