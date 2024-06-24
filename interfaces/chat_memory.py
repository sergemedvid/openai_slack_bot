from abc import ABC, abstractmethod
from typing import Dict, List

class IChatMemory(ABC):
    @abstractmethod
    def get_messages(self) -> List[Dict[str, str]]:
        pass
    
    @abstractmethod
    def format_messages(self):
        pass