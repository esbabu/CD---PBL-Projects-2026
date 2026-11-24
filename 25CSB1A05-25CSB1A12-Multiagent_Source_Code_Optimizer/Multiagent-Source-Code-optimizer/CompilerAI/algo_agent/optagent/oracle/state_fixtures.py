"""State fixture synthesis for implicit inputs: globals, files, databases, and scaling."""
from __future__ import annotations

import ast
import hashlib
import pickle
import random
from typing import Any


class StateFixtureSynthesizer:
    """Infers schemas from code usage and generates realistic state fixtures."""

    @classmethod
    def infer_and_synthesize(
        cls,
        source: str,
        size: int = 10,
        with_ties: bool = True,
        with_adjacent_dups: bool = True,
    ) -> dict[str, Any]:
        """Synthesize a complete state fixture dictionary for a given source."""
        # 1. Synthesize globals
        students = []
        # Pre-seed deterministic students with intentional ties and duplicates
        base_rolls = [101, 102, 102, 103, 104, 105, 105, 106]
        base_marks = [90, 85, 85, 95, 70, 90, 60, 80]
        base_names = ["Alice", "Bob", "Bob_Twin", "Charlie", "David", "Eve", "Frank", "Grace"]

        for i in range(size):
            r = base_rolls[i % len(base_rolls)] if i < len(base_rolls) else (100 + i)
            m = base_marks[i % len(base_marks)] if i < len(base_marks) else (50 + (i * 7) % 50)
            n = base_names[i % len(base_names)] if i < len(base_names) else f"Student_{i}"
            students.append({"name": n, "roll": r, "marks": m})

        if with_adjacent_dups and size >= 4:
            # Ensure adjacent duplicates exist for testing delete_student
            students[1]["roll"] = 102
            students[2]["roll"] = 102

        if with_ties and size >= 4:
            # Ensure ties exist for testing sorting stability
            students[0]["marks"] = 90
            students[3]["marks"] = 90

        passwords = {
            "admin": hashlib.md5("admin123".encode()).hexdigest(),
            "user1": hashlib.md5("password".encode()).hexdigest(),
        }

        # 2. Synthesize files
        files: dict[str, Any] = {}
        if "config.txt" in source:
            files["config.txt"] = "DEBUG_MODE=True\nAPP_NAME=StudentManager\nVERSION=1.0.0\n"

        if "pickle" in source:
            safe_pickle_data = pickle.dumps([
                {"name": "PickleAlice", "roll": 201, "marks": 88},
                {"name": "PickleBob", "roll": 202, "marks": 92},
            ])
            files["students.pkl"] = safe_pickle_data

        # 3. Synthesize DB
        db = {
            "schema": "CREATE TABLE IF NOT EXISTS students (username TEXT PRIMARY KEY, roll INT, marks INT, name TEXT)",
            "rows": [
                ("admin", 101, 90, "Alice"),
                ("user1", 102, 85, "Bob"),
                ("user2", 103, 95, "Charlie"),
            ],
        }

        return {
            "globals": {
                "students": students,
                "passwords": passwords,
            },
            "files": files,
            "db": db,
        }
