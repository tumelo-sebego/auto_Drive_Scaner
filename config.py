
import json

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

class Config:
    def __init__(self):
        self.config = load_config()

    def get(self, key, default=None):
        return self.config.get(key, default)
