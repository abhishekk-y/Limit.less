class UserCorrections:
    def __init__(self):
        self.corrections_log = []

    def log_correction(self, raw_input: str, user_correction: str):
        self.corrections_log.append({
            "raw": raw_input,
            "corrected": user_correction
        })

    def apply_corrections(self, data: str) -> str:
        for c in self.corrections_log:
            if data == c["raw"]:
                return c["corrected"]
        return data

if __name__ == "__main__":
    uc = UserCorrections()
    uc.log_correction("JS", "JavaScript")
    print(uc.apply_corrections("JS"))
