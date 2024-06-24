from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from interfaces.chat import IChat
from interfaces.memory_factory import IMemoryFactory

class LangchainOpenAIChat(IChat):
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