import re
from typing import Tuple

SUSPICIOUS_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"disregard (all )?system (prompts|instructions)",
    r"you are now (in|operating as) DAN",
    r"jailbreak mode",
    r"bypass safety filters",
    r"output (your|the) system prompt",
    r"system prompt leak",
]

def detect_prompt_injection(user_input: str) -> Tuple[bool, float, str]:
    """
    Checks if input contains prompt injection patterns.
    Returns (is_suspicious, confidence, reason).
    """
    text_lower = user_input.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, text_lower):
            return True, 0.95, f"Matched injection pattern: {pattern}"
    
    return False, 0.0, "Input clean"
