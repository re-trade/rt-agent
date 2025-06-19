class OffensiveDetect:
    def __init__(self, file_path: str):
        self.prohibited_words = set()
        self.load_prohibited_words(file_path)

    def load_prohibited_words(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            self.prohibited_words = set(file.read().splitlines())  # Use a set for fast lookup

    def contains_prohibited_words(self, text: str) -> bool:
        words = text.lower().split()  # Tokenize input
        return any(word in self.prohibited_words for word in words)

