#!/usr/bin/env python3
import json

class HistoryManager:
    def __init__(self):
        self.history_file = "game_history.json"
        self.load_history()

    def load_history(self):
        try:
            with open(self.history_file, "r") as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []

    def save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=4)

    def record_game(self, game_data):
        self.history.append(game_data)
        self.save_history()
