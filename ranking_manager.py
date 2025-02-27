#!/usr/bin/env python3
import json

class RankingManager:
    def __init__(self):
        self.ranking_file = "ranking.json"
        self.load_ranking()

    def load_ranking(self):
        try:
            with open(self.ranking_file, "r") as f:
                self.ranking = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ranking = {}

    def save_ranking(self):
        with open(self.ranking_file, "w") as f:
            json.dump(self.ranking, f, indent=4)

    def update_ranking(self, winner_name):
        if winner_name not in self.ranking:
            self.ranking[winner_name] = 0
        self.ranking[winner_name] += 1
        self.save_ranking()
