class IWebServer:
    def run(self, port: int):
        pass

    def add_route(self, endpoint: str, view_func, methods: list):
        pass
    
    def get_app(self):
        pass