from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from interfaces.chat import IChat

class OpenAIChat(IChat):
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.chat_model = ChatOpenAI(model_name='gpt-4o', openai_api_key=self.openai_api_key)
        with open("assistant_prompt_template.txt") as f:
            template = f.read()
        prompt = PromptTemplate(input_variables=["history", "input"], template=template)
        memory = ConversationBufferWindowMemory(k=3, memory_key="history")
        self.chat_chain = ConversationChain(memory=memory, llm=self.chat_model, prompt=prompt, verbose=True)

    def get_response(self, input_text):
        return self.chat_chain.predict(input=input_text)
