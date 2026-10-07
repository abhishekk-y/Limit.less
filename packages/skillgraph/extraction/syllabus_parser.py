import re

class SyllabusParser:
    def __init__(self):
        self.skill_keywords = ["Python", "Java", "C++", "Data Structures", "Algorithms", "Machine Learning"]

    def parse(self, text: str) -> list:
        found_skills = []
        for skill in self.skill_keywords:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        return found_skills

if __name__ == "__main__":
    parser = SyllabusParser()
    print(parser.parse("Course covers Python and Machine Learning fundamentals."))
