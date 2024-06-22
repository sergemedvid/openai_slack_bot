# app.py
from slack_bot import SlackBot
from chat.openai import OpenAIChat
from dotenv import load_dotenv
import os

from web_server.flask import FlaskWebServer

if __name__ == "__main__":
    load_dotenv()
    chat_service = OpenAIChat(openai_api_key = os.environ["OPENAI_API_KEY"])
    web_server = FlaskWebServer()
    bot = SlackBot(chat_service=chat_service, web_server=web_server,
                   slack_bot_token=os.environ["SLACK_BOT_TOKEN"], signing_secret=os.environ["SIGNING_SECRET"])
    bot.run()