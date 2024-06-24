from chat.langchain_slack_thread_memory import LangchainSlackThreadMemory
from chat.slack_thread_memory import SlackThreadMemory
from interfaces.memory_factory import IMemoryFactory


from langchain.memory import ConversationBufferWindowMemory

from slack_bot import SlackBot


class LangchainBufferWindowMemoryFactory(IMemoryFactory):
    def __init__(self, k, memory_key):
        self.k = k
        self.memory_key = memory_key

    def create_memory(self):
        return ConversationBufferWindowMemory(k=self.k, memory_key=self.memory_key)


class LangchainSlackThreadMemoryFactory(IMemoryFactory):
    def __init__(self, memory_key, slack_bot: SlackBot):
        self.memory_key = memory_key
        self.slack_bot = slack_bot

    def create_memory(self):
        return LangchainSlackThreadMemory(memory_key=self.memory_key, slack_bot=self.slack_bot)
    
class SlackThreadMemoryFactory(IMemoryFactory):
    def __init__(self, memory_key, slack_bot: SlackBot):
        self.memory_key = memory_key
        self.slack_bot = slack_bot

    def create_memory(self):
        return SlackThreadMemory(memory_key=self.memory_key, slack_bot=self.slack_bot)