import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TypedDict
from mcp_council_of_mine.security import (
    validate_debate_id,
    sanitize_text,
)


class Opinion(TypedDict):
    member_id: int
    member_name: str
    opinion: str


class Vote(TypedDict):
    voter_id: int
    voted_for_id: int
    reasoning: str


class DebateState(TypedDict):
    debate_id: str
    prompt: str
    timestamp: str
    opinions: dict[int, Opinion]
    votes: dict[int, Vote]
    results: dict | None


class StateManager:
    def __init__(self, debates_dir: str = "debates"):
        self.debates_dir = Path(debates_dir)
        self.debates_dir.mkdir(exist_ok=True)
        self.current_debate: DebateState | None = None

    def start_new_debate(self, prompt: str) -> str:
        timestamp = datetime.now()
        debate_id = timestamp.strftime("%Y%m%d_%H%M%S")

        self.current_debate = {
            "debate_id": debate_id,
            "prompt": prompt,
            "timestamp": timestamp.isoformat(),
            "opinions": {},
            "votes": {},
            "results": None
        }

        return debate_id

    def add_opinion(self, member_id: int, member_name: str, opinion: str):
        if not self.current_debate:
            raise ValueError("No active debate. Call start_new_debate first.")

        self.current_debate["opinions"][member_id] = {
            "member_id": member_id,
            "member_name": member_name,
            "opinion": sanitize_text(opinion, max_length=2000)
        }

    def add_vote(self, voter_id: int, voted_for_id: int, reasoning: str):
        if not self.current_debate:
            raise ValueError("No active debate. Call start_new_debate first.")

        if voter_id == voted_for_id:
            raise ValueError("Members cannot vote for themselves")

        self.current_debate["votes"][voter_id] = {
            "voter_id": voter_id,
            "voted_for_id": voted_for_id,
            "reasoning": sanitize_text(reasoning, max_length=1000)
        }

    def set_results(self, results: dict):
        if not self.current_debate:
            raise ValueError("No active debate. Call start_new_debate first.")

        self.current_debate["results"] = results

    def save_current_debate(self):
        if not self.current_debate:
            raise ValueError("No active debate to save")

        debate_id = self.current_debate["debate_id"]
        file_path = self.debates_dir / f"{debate_id}.json"

        with open(file_path, 'w') as f:
            json.dump(self.current_debate, f, indent=2)

        return str(file_path)

    def load_debate(self, debate_id: str) -> DebateState:
        if not validate_debate_id(debate_id):
            raise ValueError("Invalid debate_id format. Expected: YYYYMMDD_HHMMSS")

        file_path = self.debates_dir / f"{debate_id}.json"

        try:
            resolved_path = file_path.resolve()
            debates_dir_resolved = self.debates_dir.resolve()

            if not resolved_path.is_relative_to(debates_dir_resolved):
                logging.error(f"Path traversal attempt detected: {debate_id}")
                raise ValueError("Invalid debate_id: path traversal detected")
        except (ValueError, OSError) as e:
            logging.error(f"Path validation failed for debate_id {debate_id}: {e}")
            raise ValueError("Invalid debate_id")

        if not file_path.exists():
            raise FileNotFoundError(f"Debate {debate_id} not found")

        try:
            with open(file_path, 'r') as f:
                debate = json.load(f)
        except json.JSONDecodeError:
            logging.error(f"Corrupted debate file: {debate_id}")
            raise ValueError("Debate file is corrupted")

        logging.info(f"Successfully loaded debate: {debate_id}")
        return debate

    def list_debates(self) -> list[dict]:
        debate_files = sorted(self.debates_dir.glob("*.json"), reverse=True)
        debates = []

        for file_path in debate_files:
            try:
                with open(file_path, 'r') as f:
                    debate = json.load(f)
                    debates.append({
                        "debate_id": debate["debate_id"],
                        "prompt": debate["prompt"],
                        "timestamp": debate["timestamp"],
                        "has_results": debate.get("results") is not None
                    })
            except (json.JSONDecodeError, KeyError) as e:
                logging.warning(f"Skipping invalid debate file {file_path}: {e}")
                continue

        return debates

    def get_current_debate(self) -> DebateState | None:
        return self.current_debate

    def clear_current_debate(self):
        self.current_debate = None


_state_manager = StateManager()


def get_state_manager() -> StateManager:
    return _state_manager
