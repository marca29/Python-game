import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "storage.json")

class StateManager:
    def __init__(self):
        self.state = {
            "players": [],
            "matches": [],
            "statistics": {}
        }
        self.load()

    def load(self):
        if not os.path.exists(STATE_FILE):
            self.save()
            return

        try:
            with open(STATE_FILE, "r") as f:
                self.state = json.load(f)
        except Exception:
            self.state = {
                "players": [],
                "matches": [],
                "statistics": {}
            }
            self.save()

    def save(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=2)

state_manager = StateManager()