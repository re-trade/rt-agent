import re
from pathlib import Path

class OffensiveDetect:
    def __init__(self, file_path: Path):
        self.prohibited_words = set()
        self.load_prohibited_words(file_path)

    def load_prohibited_words(self, file_path: Path):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.prohibited_words = set(line.strip().lower() for line in file if line.strip())

    def contains_prohibited_words(self, text: str) -> bool:
        # Tách từ bằng regex để loại bỏ dấu câu
        words = re.findall(r'\w+', text.lower())
        return any(word in self.prohibited_words for word in words)
