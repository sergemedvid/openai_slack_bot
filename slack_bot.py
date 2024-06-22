# slack_bot.py
import os
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from interfaces.chat import IChat
from interfaces.web_server import IWebServer

class SlackBot:
    MAX_MESSAGE_LENGTH = 4000

    def __init__(self, chat_service: IChat, web_server: IWebServer, slack_bot_token: str, signing_secret: str):
        self.slack_bot_token = slack_bot_token
        self.signing_secret = signing_secret
        self.app = App(token=self.slack_bot_token, signing_secret=self.signing_secret)
        self.web_server = web_server
        self.handler = SlackRequestHandler(self.app)
        self.chat_service = chat_service
        self._register_events()

    def _register_events(self):
        self.app.event("app_mention")(self.handle_app_mentions)
        self.app.event("message")(self.handle_message_events)
        self.web_server.add_route("/slack/events", self.slack_events, ["POST"])

    def process_slack_event(self, say, user_id, channel_id, thread_ts, text):
        result = say(text="Thinking... please wait", thread_ts=thread_ts, mrkdwn=True)
        thinking_message_ts = result["ts"]
        response = self.chat_service.get_response(input_text=text)
        # Directly call send_message with the entire response and thinking_message_ts
        self.send_message(channel_id, user_id, thread_ts, response, thinking_message_ts)

    def send_message(self, channel_id, user_id, thread_ts, text, message_ts=None):
        paragraphs = text.split("\n\n")
        current_message = ""
        first_chunk_sent = False
        for paragraph in paragraphs:
            if len(current_message) + len(paragraph) + 1 > SlackBot.MAX_MESSAGE_LENGTH:
                if not first_chunk_sent and message_ts:
                    # Update the thinking message with the first chunk
                    self.app.client.chat_update(channel=channel_id, ts=message_ts, text=current_message, thread_ts=thread_ts)
                    first_chunk_sent = True
                else:
                    # Send the current message if it reaches the limit
                    self.app.client.chat_postMessage(channel=channel_id, text=current_message, thread_ts=thread_ts, mrkdwn=True)
                current_message = paragraph  # Start a new message
            else:
                if current_message:
                    current_message += "\n\n"
                current_message += paragraph
        # Send any remaining message
        if current_message:
            if not first_chunk_sent and message_ts:
                # Update the thinking message if it's the first chunk
                self.app.client.chat_update(channel=channel_id, ts=message_ts, text=current_message, thread_ts=thread_ts)
            else:
                # Otherwise, send as a new message
                self.app.client.chat_postMessage(channel=channel_id, text=current_message, thread_ts=thread_ts)

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
