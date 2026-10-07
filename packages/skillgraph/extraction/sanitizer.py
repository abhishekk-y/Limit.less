import re
from typing import Dict, Any, Tuple, Optional, List

class DocumentSanitizer:
    """Detect hidden text, prompt injection, and keyword stuffing in untrusted docs."""
    
    INJECTION_PATTERNS = [
        r"ignore (all )?previous instructions",
        r"you are now (a )?bot",
        r"bypass (the )?system",
        r"system prompt",
        r"forget everything"
    ]

    def __init__(self):
        self.injection_regex = re.compile("|".join(self.INJECTION_PATTERNS), re.IGNORECASE)

    def detect_hidden_text(self, text: str, html_content: Optional[str] = None) -> bool:
        """Detect hidden text (e.g., white text on white background if HTML, or zero-width chars)."""
        if html_content:
            if re.search(r'color:\s*(white|#ffffff|#fff|transparent).*?background', html_content, re.IGNORECASE):
                return True
        # Check for zero-width characters (e.g. U+200B)
        if '\u200b' in text or '\u200c' in text or '\u200d' in text:
            return True
        return False

    def detect_prompt_injection(self, text: str) -> Tuple[bool, float]:
        """Detect attempts to inject prompts. Returns (is_injection, confidence)."""
        matches = self.injection_regex.findall(text)
        if matches:
            return True, min(1.0, len(matches) * 0.3)
        return False, 0.0

    def detect_keyword_stuffing(self, text: str, keywords: List[str]) -> Tuple[bool, float]:
        """Detect keyword stuffing by measuring density."""
        words = text.lower().split()
        if not words:
            return False, 0.0
            
        keyword_counts = {kw: text.lower().count(kw.lower()) for kw in keywords}
        total_keyword_mentions = sum(keyword_counts.values())
        
        density = total_keyword_mentions / len(words)
        # Threshold for stuffing, e.g., > 10%
        is_stuffing = density > 0.10
        return is_stuffing, density

    def sanitize(self, text: str, keywords: List[str], html_content: Optional[str] = None) -> Dict[str, Any]:
        """Run all sanitation checks."""
        has_hidden = self.detect_hidden_text(text, html_content)
        has_injection, inj_conf = self.detect_prompt_injection(text)
        has_stuffing, stuff_density = self.detect_keyword_stuffing(text, keywords)
        
        return {
            "is_safe": not (has_hidden or has_injection or has_stuffing),
            "flags": {
                "hidden_text": has_hidden,
                "prompt_injection": has_injection,
                "keyword_stuffing": has_stuffing
            },
            "metrics": {
                "injection_confidence": inj_conf,
                "stuffing_density": stuff_density
            }
        }
