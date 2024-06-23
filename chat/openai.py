from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from chat.slack_thread_memory import SlackThreadMemory
from interfaces.chat import IChat
from interfaces.memory_factory import IMemoryFactory
from slack_bot import SlackBot

class BufferWindowMemoryFactory(IMemoryFactory):
    def __init__(self, k, memory_key):
        self.k = k
        self.memory_key = memory_key

    def create_memory(self):
        return ConversationBufferWindowMemory(k=self.k, memory_key=self.memory_key)

class SlackThreadMemoryFactory(IMemoryFactory):
    def __init__(self, memory_key, slack_bot: SlackBot):
        self.memory_key = memory_key
        self.slack_bot = slack_bot
    
    def create_memory(self):
        return SlackThreadMemory(memory_key=self.memory_key, slack_bot=self.slack_bot)

class OpenAIChat(IChat):
    def __init__(self, openai_api_key: str, memory_factory: IMemoryFactory):
        self.openai_api_key = openai_api_key
        self.chat_model = ChatOpenAI(model_name='gpt-4o', openai_api_key=self.openai_api_key)
        with open("assistant_prompt_template.txt") as f:
            template = f.read()
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        self.memory = memory_factory.create_memory()
        
        self.chat_chain = ConversationChain(memory=self.memory, llm=self.chat_model, prompt=prompt, verbose=True)

    def get_response(self, input_text):
        return self.chat_chain.predict(input=input_text)

    def get_memory(self):
        return self.memory