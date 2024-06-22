# app.py
from slack_bot import SlackBot
from openai_chat import OpenAIChat
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    chat_service = OpenAIChat(openai_api_key = os.environ["OPENAI_API_KEY"])
    bot = SlackBot(chat_service=chat_service, slack_bot_token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SIGNING_SECRET"])
    bot.run()