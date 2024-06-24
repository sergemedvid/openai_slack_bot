import threading
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from interfaces.chat import IChat
from interfaces.web_server import IWebServer

class SlackBot:
    MAX_MESSAGE_LENGTH = 4000
    THINKING_MESSAGE = "Thinking... please wait"  # New constant for the "Thinking..." string

    def __init__(self, chat_service: IChat, web_server: IWebServer, slack_bot_token: str, signing_secret: str):
        self.slack_bot_token = slack_bot_token
        self.signing_secret = signing_secret
        self.app = App(token=self.slack_bot_token, signing_secret=self.signing_secret)
        self.web_server = web_server
        self.handler = SlackRequestHandler(self.app)
        self.chat_service = chat_service
        self.lock = threading.Lock()  # Initialize the lock
        self._fetch_and_store_bot_user_id()
        self._register_events()

    def _fetch_and_store_bot_user_id(self):
        response = self.app.client.auth_test()
        if response["ok"]:
            self.bot_user_id = response["user_id"]
        else:
            self.bot_user_id = None

    def _register_events(self):
        self.app.event("app_mention")(self.handle_app_mentions)
        self.app.event("message")(self.handle_message_events)
        self.web_server.add_route("/slack/events", self.slack_events, ["POST"])

    def process_slack_event(self, say, user_id, channel_id, thread_ts, text):
        with self.lock:  # Acquire the lock
            # Save state
            self.channel_id = channel_id
            self.thread_ts = thread_ts
            self.user_id = user_id
            self.say = say
            result = say(text=SlackBot.THINKING_MESSAGE, thread_ts=thread_ts, mrkdwn=True)
            thinking_message_ts = result["ts"]
            response = self.chat_service.get_response(input_text=text)
            # Directly call send_message with the entire response and thinking_message_ts
            self.send_message(channel_id, user_id, thread_ts, response, thinking_message_ts)
            # Clear state
            self.channel_id = None
            self.thread_ts = None
            self.user_id = None
            self.say = None

    def get_messages(self, channel_id, thread_ts):
        messages = self.app.client.conversations_replies(channel=channel_id, ts=thread_ts)
        # Filter out messages containing the THINKING_MESSAGE
        filtered_messages = [msg for msg in messages['messages'] if msg.get('text', '') != SlackBot.THINKING_MESSAGE]
        return {"messages": filtered_messages}
    
    def get_current_event_messages(self):
        if self.channel_id and self.thread_ts:
            return self.get_messages(self.channel_id, self.thread_ts)
        else:
            return None

    def get_bot_user_id(self):
        return self.bot_user_id

    def send_message(self, channel_id, user_id, thread_ts, text, message_ts=None):
        if message_ts:
            # Delete the "Thinking..." message
            self.app.client.chat_delete(channel=channel_id, ts=message_ts, as_user=True)
        
        paragraphs = text.split("\n\n")
        current_message = ""
        for paragraph in paragraphs:
            if len(current_message) + len(paragraph) + 1 > SlackBot.MAX_MESSAGE_LENGTH:
                # Send the current message if it reaches the limit
                self.app.client.chat_postMessage(channel=channel_id, text=current_message, thread_ts=thread_ts, mrkdwn=True)
                current_message = paragraph  # Start a new message
            else:
                if current_message:
                    current_message += "\n\n"
                current_message += paragraph
        # Send any remaining message
        if current_message:
            self.app.client.chat_postMessage(channel=channel_id, text=current_message, thread_ts=thread_ts, mrkdwn=True)

    def handle_app_mentions(self, body, say, logger):
        self._handle_event(body, say, logger)

    def handle_message_events(self, body, say, logger):
        self._handle_event(body, say, logger)

    def _handle_event(self, body, say, logger):
        # Skip deleted/changed messages
        if body["event"].get("subtype") == "message_changed" or body["event"].get("subtype") == "message_deleted":
            return
        
        user_id = body["event"]["user"]
        channel_id = body["event"]["channel"]
        event_ts = body["event"].get("ts")
        thread_ts = body["event"].get("thread_ts") or event_ts
        text = body["event"]["text"]
        self.process_slack_event(say, user_id, channel_id, thread_ts, text)

    def slack_events(self):
        return self.handler.handle(request)
