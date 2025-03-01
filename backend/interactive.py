import re
import json
from typing import List, Dict, Optional
from pathlib import Path

class QuizGenerator:
    def __init__(self):
        self.structured_dir = Path("backend/structured")

    def get_available_files(self) -> List[str]:
        """Get list of available structured data files"""
        if not self.structured_dir.exists():
            return []
        return [f.name for f in self.structured_dir.glob("*.txt")]

    def load_questions(self, file_name: str) -> List[Dict]:
        """Load and parse questions from a structured data file"""
        file_path = self.structured_dir / file_name
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                questions = json.loads(f.read())
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in file: {file_path}")

        return questions

    def validate_answer(self, question: Dict, answer: str) -> bool:
        """Validate if the given answer is correct"""
        return answer.startswith(question['correct_answer'])
