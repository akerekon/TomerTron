import os
from waitress import serve
from bot import flask_app

if __name__ == "__main__":
    serve(flask_app, host=os.getenv("SERVER_IP"), port=os.getenv("SERVER_PORT"))