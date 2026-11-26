"""Medical safety disclaimers and emergency warning detection."""

import re
from typing import List, Tuple

GENERAL_DISCLAIMER = (
    "Educational Use Only: AI Medical Assistant does not provide medical diagnoses, "
    "prescribe medications, or replace care from a licensed healthcare professional."
)

REPORT_DISCLAIMER = (
    "Report Summary Disclaimer: This plain-language summary is for educational reference only. "
    "Only values and reference ranges present in your uploaded report are shown; verify all "
    "laboratory results with your ordering clinician."
)

IMAGE_DISCLAIMER = (
    "Medical Image Limitation Notice: AI visual observations are strictly informational and are "
    "NOT a medical diagnosis. Images cannot replace a clinical exam or review by a radiologist "
    "or specialist."
)

EMERGENCY_GUIDANCE = (
    "Potential Emergency Warning Signs Detected: Please call your local emergency number "
    "(such as 911 in the US, 112 in the EU/India, or 999 in the UK) or go to the nearest "
    "emergency department immediately."
)

_EMERGENCY_PATTERNS: List[Tuple[str, str]] = [
    (r"\bchest\s+pain\b|\bchest\s+tightness\b|\bcrushing\s+chest\b", "Chest pain or pressure"),
    (
        r"\bshortness\s+of\s+breath\b|\bcan(?:'|no)?t\s+breathe\b|\bdifficulty\s+breathing\b|\btrouble\s+breathing\b",
        "Severe breathing difficulty",
    ),
    (
        r"\bsuicid(?:e|al)\b|\bkill\s+myself\b|\bself[-\s]?harm\b|\bwant\s+to\s+die\b",
        "Mental health crisis / self-harm risk",
    ),
    (
        r"\bface\s+drooping\b|\bslurred\s+speech\b|\barm\s+weakness\b|\bsudden\s+numbness\b|\bstroke\b",
        "Possible stroke warning signs",
    ),
    (
        r"\bsevere\s+bleeding\b|\buncontrolled\s+bleeding\b|\bcoughing\s+up\s+blood\b|\bvomiting\s+blood\b",
        "Severe or unusual bleeding",
    ),
    (
        r"\bunconscious\b|\bpassed\s+out\b|\bfainting\b|\bseizure\b|\bconvulsion\b",
        "Loss of consciousness or seizure",
    ),
    (
        r"\banaphylaxis\b|\bthroat\s+swelling\b|\btongue\s+swelling\b|\bsevere\s+allergic\s+reaction\b",
        "Possible severe allergic reaction",
    ),
    (r"\boverdose\b|\bpoisoning\b", "Possible overdose or poisoning"),
]


def detect_emergency_signals(text: str) -> Tuple[bool, List[str]]:
    """Inspect user-supplied text for red-flag emergency symptoms."""
    normalized = (text or "").lower()
    reasons: List[str] = []
    for pattern, label in _EMERGENCY_PATTERNS:
        if re.search(pattern, normalized):
            reasons.append(label)
    return bool(reasons), reasons
