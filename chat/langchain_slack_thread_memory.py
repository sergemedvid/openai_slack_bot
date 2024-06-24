from typing import Any, Dict, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain.memory.chat_memory import BaseChatMemory
from pydantic import Field

from slack_bot import SlackBot

class LangchainSlackThreadMemory(BaseChatMemory):
    slack_bot: SlackBot = Field(...)
    memory_key: str = Field(...)
    
    def fetch_slack_messages(self) -> List[HumanMessage]:
        response = self.slack_bot.get_current_event_messages()
        messages = []
        for msg in response['messages']:
            # Assuming all messages from the bot are AI responses and others are human messages
            if msg.get('user') == self.slack_bot.get_bot_user_id():
                messages.append(AIMessage(content=msg['text']))
            else:
                messages.append(HumanMessage(content=msg['text']))
        # Remove last human message as we use it to get the input, but only if there's at least one
        if messages and isinstance(messages[-1], HumanMessage):
            messages.pop()
        return messages

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        messages = self.fetch_slack_messages()
        # Initialize formatted_messages as an empty string
        formatted_messages = ""
        # Iterate over each message and format it
        for message in messages:
            if isinstance(message, AIMessage):
                formatted_messages += "Assistant: " + message.content + "\n"
            else:
                formatted_messages += "Human: " + message.content + "\n"
        # Remove the last newline character
        formatted_messages = formatted_messages.rstrip('\n')
        return {'history': formatted_messages}