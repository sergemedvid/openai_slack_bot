from interfaces.chat import IChat
from openai import OpenAI

from interfaces.memory_factory import IMemoryFactory

class OpenAIChat(IChat):
    SYSTEM_PROMPT = """You're an AI assistant communicating in Slack."""

    def __init__(self, openai_api_key: str, memory_factory: IMemoryFactory):
        self.openai_api_key = openai_api_key
        self.memory = memory_factory.create_memory()
        self.client = OpenAI(api_key=self.openai_api_key)

    def get_response(self, input_text: str) -> str:
        # Retrieve structured messages from memory
        structured_messages = self.memory.get_messages()
        
        # Convert structured messages to the format expected by OpenAI API
        messages_for_openai = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        for msg in structured_messages:
            role = "assistant" if msg["type"] == "Assistant" else "user"
            messages_for_openai.append({"role": role, "content": msg["content"]})
        
        # Append the current input text as the latest message from the user
        messages_for_openai.append({"role": "user", "content": input_text})
        print(messages_for_openai)
        
        # Call the OpenAI API with the prepared messages
        response = self.client.chat.completions.create(model="gpt-4o", messages=messages_for_openai)
        
        # Return the response content if available, otherwise return "No response"
        return response.choices[0].message.content if response.choices else "No response"