from uvicorn import Server, Config

from news.api.crawler import crawler_app
from news.settings import HOST, PORT


def run_server():
    config = Config(app=crawler_app, host=HOST, port=PORT)
    server = Server(config=config)

    server.run()
