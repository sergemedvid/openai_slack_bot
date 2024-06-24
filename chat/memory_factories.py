from chat.slack_thread_memory import SlackThreadMemory
from interfaces.memory_factory import IMemoryFactory


from slack_bot import SlackBot


class SlackThreadMemoryFactory(IMemoryFactory):
    def __init__(self, memory_key, slack_bot: SlackBot):
        self.memory_key = memory_key
        self.slack_bot = slack_bot

    def create_memory(self):
        return SlackThreadMemory(memory_key=self.memory_key, slack_bot=self.slack_bot)