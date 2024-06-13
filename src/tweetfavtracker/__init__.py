import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # 環境変数を設定
    app.config["AUTH_TOKEN"] = os.getenv("AUTH_TOKEN")
    app.config["CT0"] = os.getenv("CT0")
    app.config["BEARER_TOKEN"] = os.getenv("BEARER_TOKEN")
    app.config["SCREEN_NAME"] = os.getenv("SCREEN_NAME")

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
