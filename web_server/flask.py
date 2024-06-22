from flask import Flask, request

from interfaces.web_server import IWebServer

class FlaskWebServer(IWebServer):
    def __init__(self):
        self.app = Flask(__name__)
        
    def get_app(self):
        return self.app

    def run(self, port: int):
        self.app.run(port=port)

    def add_route(self, endpoint: str, view_func, methods: list):
        self.app.route(endpoint, methods=methods)(view_func)
