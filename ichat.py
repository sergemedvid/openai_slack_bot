from abc import ABC, abstractmethod

class IChat(ABC):
    @abstractmethod
    def get_response(self, input_text):
        pass