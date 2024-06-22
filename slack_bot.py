import os
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from openai_chat import OpenAIChat

class SlackBot:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
        self.signing_secret = os.environ["SIGNING_SECRET"]
        self.app = App(token=self.slack_bot_token, signing_secret=self.signing_secret)
        self.flask_app = Flask(__name__)
        self.handler = SlackRequestHandler(self.app)
        self.openai_chat = OpenAIChat()
        self._register_events()

    def _register_events(self):
        self.app.event("app_mention")(self.handle_app_mentions)
        self.app.event("message")(self.handle_message_events)
        self.flask_app.route("/slack/events", methods=["POST"])(self.slack_events)

    def process_slack_event(self, say, user_id, channel_id, thread_ts, text):
        result = say(text="Thinking... please wait", thread_ts=thread_ts)
        thinking_message_ts = result["ts"]
        response = self.openai_chat.get_response(input_text=text)
        self.app.client.chat_update(channel=channel_id, ts=thinking_message_ts, text=f"Hi there, <@{user_id}>!\n{response}", thread_ts=thread_ts)

    def handle_app_mentions(self, body, say, logger):
        self._handle_event(body, say, logger)

    def handle_message_events(self, body, say, logger):
        self._handle_event(body, say, logger)

    def _handle_event(self, body, say, logger):
        user_id = body["event"]["user"]
        channel_id = body["event"]["channel"]
        event_ts = body["event"].get("ts")
        thread_ts = body["event"].get("thread_ts") or event_ts
        text = body["event"]["text"]
        self.process_slack_event(say, user_id, channel_id, thread_ts, text)

    def slack_events(self):
        return self.handler.handle(request)

    def run(self):
        self.flask_app.run(port=5001)