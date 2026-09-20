"""Lightweight cross-run agent memory backed by a local JSON file."""

import json
import os


class AgentMemory:
    def __init__(self, path: str = "data/memory.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def load(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path) as f:
            return json.load(f)

    def save(self, key: str, value) -> None:
        data = self.load()
        data[key] = value
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)
