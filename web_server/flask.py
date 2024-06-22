from flask import Flask, request

from interfaces.webserver import IWebServer

class FlaskWebServer(IWebServer):
    def __init__(self):
        self.app = Flask(__name__)

    def run(self, port: int):
        self.app.run(port=port)

    def add_route(self, endpoint: str, view_func, methods: list):
        self.app.route(endpoint, methods=methods)(view_func)
