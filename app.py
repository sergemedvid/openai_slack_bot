from chat.memory_factories import LangchainBufferWindowMemoryFactory, LangchainSlackThreadMemoryFactory
from slack_bot import SlackBot
from chat.langchain_openai import LangchainOpenAIChat
from dotenv import load_dotenv
import os

from web_server.flask import FlaskWebServer

# Load environment variables
load_dotenv()

def initialize_services():
    web_server = FlaskWebServer()
    bot = SlackBot(chat_service=None, web_server=web_server,
                   slack_bot_token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SIGNING_SECRET"])

    memory_factory = LangchainSlackThreadMemoryFactory(memory_key="history", slack_bot=bot)
    #memory_factory = BufferWindowMemoryFactory(k=5, memory_key="history")
    chat_service = LangchainOpenAIChat(openai_api_key=os.environ["OPENAI_API_KEY"], memory_factory=memory_factory)

    # Link the chat_service back to the bot
    bot.chat_service = chat_service

    return web_server, bot

# Get the Flask app instance through the initialization function
web_server, bot = initialize_services()
app = web_server.get_app()

if __name__ == "__main__":
    # When called directly, run the Flask development server
    web_server.run(port=5001)