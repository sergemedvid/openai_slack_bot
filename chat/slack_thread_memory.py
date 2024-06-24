from typing import Dict, List
from pydantic import Field
from slack_bot import SlackBot


class SlackThreadMemory:
    slack_bot: SlackBot = Field(...)
    memory_key: str = Field(...)
    
    def fetch_slack_messages(self) -> List[Dict[str, str]]:
        response = self.slack_bot.get_current_event_messages()
        messages = []
        for msg in response['messages']:
            user_type = "Assistant" if msg.get('user') == self.slack_bot.get_bot_user_id() else "Human"
            messages.append({"type": user_type, "content": msg['text']})
        if messages and messages[-1]["type"] == "Human":
            messages.pop()
        return messages

    def format_messages(self, messages: List[Dict[str, str]]) -> str:
        formatted_messages = ""
        for message in messages:
            formatted_messages += f"{message['type']}: {message['content']}\n"
        return formatted_messages.rstrip('\n')