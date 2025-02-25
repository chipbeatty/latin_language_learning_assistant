import re
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
            questions_data = f.read()

        questions = []
        question_blocks = re.findall(r'<question>(.*?)</question>', questions_data, re.DOTALL)

        for block in question_blocks:
            # Extract parts
            intro = re.search(r'Introduction:\s*(.+?)(?=\n\s*Conversation:|$)', block, re.DOTALL)
            conv = re.search(r'Conversation:\s*(.+?)(?=\n\s*Question:|$)', block, re.DOTALL)
            q = re.search(r'Question:\s*(.+?)$', block, re.DOTALL)

            if q:  # Only need the question part for now
                question_text = q.group(1).strip()
                # Extract the correct answer from the question
                correct_answer = question_text.split('?')[0] + "."
                
                # Generate plausible wrong answers
                wrong_answers = [
                    "Une réponse incorrecte mais plausible.",
                    "Une autre option qui semble possible.",
                    "Une troisième suggestion intéressante."
                ]
                
                # Randomly assign letters to answers
                import random
                answers = [correct_answer] + wrong_answers
                random.shuffle(answers)
                
                # Create choices with letters
                choices = [f"{chr(65+i)}) {answer}" for i, answer in enumerate(answers)]
                
                # Find which letter corresponds to the correct answer
                correct_letter = chr(65 + answers.index(correct_answer))
                
                questions.append({
                    'question': question_text,
                    'choices': choices,
                    'correct_answer': correct_letter,
                    'topic': 'Conversation'
                })

        return questions

    def validate_answer(self, question: Dict, answer: str) -> bool:
        """Validate if the given answer is correct"""
        return answer.startswith(question['correct_answer'])
