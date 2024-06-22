from slack_bot import SlackBot
from chat.openai import OpenAIChat
from dotenv import load_dotenv
import os

from web_server.flask import FlaskWebServer

# Load environment variables
load_dotenv()

# Initialize services
chat_service = OpenAIChat(openai_api_key=os.environ["OPENAI_API_KEY"])
web_server = FlaskWebServer()
bot = SlackBot(chat_service=chat_service, web_server=web_server,
               slack_bot_token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SIGNING_SECRET"])

# Get the Flask app instance
app = web_server.get_app()

if __name__ == "__main__":
    # When called directly, run the Flask development server
    web_server.run(port=5001)