import os
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate

# Load the environment variables
load_dotenv(find_dotenv())

slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
openai_api_key = os.environ["OPENAI_API_KEY"]
signing_secret = os.environ["SIGNING_SECRET"]

app = App(token=slack_bot_token, signing_secret=signing_secret)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

CHATAI = ChatOpenAI(model_name='gpt-4o', openai_api_key=openai_api_key)

with open("assistant_prompt_template.txt") as f:
    template = f.read()
prompt = PromptTemplate(input_variables=["history", "input"], template=template)
memory = ConversationBufferWindowMemory(k=3, memory_key="history")
chat_chain = ConversationChain(memory=memory, llm=CHATAI, prompt=prompt,verbose=True)

@app.event("app_mention")
def handle_app_mentions(body, say, logger):
    user_id = body["event"]["user"]
    event_ts = body["event"].get("ts")
    thread_ts = body["event"].get("thread_ts")

    # If the message is not in a thread, reply in a thread.
    if not thread_ts:
        thread_ts = event_ts

    text = body["event"]["text"]
    response = chat_chain.predict(input=text)
    say(text=f"Hi there, <@{user_id}>!\n{response}", thread_ts=thread_ts)

@app.event("message")
def handle_message_events(body, say, logger):
    user_id = body["event"]["user"]
    event_ts = body["event"].get("ts")
    thread_ts = body["event"].get("thread_ts")

    # If the message is not in a thread, reply in a thread.
    if not thread_ts:
        thread_ts = event_ts

    text = body["event"]["text"]
    response = chat_chain.predict(input=text)
    say(text=f"Hi there, <@{user_id}>!\n{response}", thread_ts=thread_ts)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(port=5001)