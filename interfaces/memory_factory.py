from abc import ABC, abstractmethod

class IMemoryFactory(ABC):
    @abstractmethod
    def create_memory(self):
        pass