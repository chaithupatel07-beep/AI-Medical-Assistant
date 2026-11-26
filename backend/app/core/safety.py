"""Multilingual medical safety disclaimers and emergency warning detection (EN, TE, HI)."""

import re
from typing import Dict, List, Tuple

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
    "(such as 911 in the US, 112 in India/EU, or 999 in the UK) or go to the nearest "
    "emergency department immediately."
)

DISCLAIMERS_BY_LANG: Dict[str, Dict[str, str]] = {
    "en": {
        "general": GENERAL_DISCLAIMER,
        "report": REPORT_DISCLAIMER,
        "image": IMAGE_DISCLAIMER,
        "emergency": EMERGENCY_GUIDANCE,
    },
    "te": {
        "general": (
            "విద్యా సమాచారం మాత్రమే: AI మెడికల్ అసిస్టెంట్ వైద్య నిర్ధారణలు చేయదు, "
            "మందులు సూచించదు మరియు అర్హత కలిగిన డాక్టర్ చికిత్సకు ప్రత్యామ్నాయం కాదు."
        ),
        "report": (
            "రిపోర్ట్ సారాంశ గమనిక: ఈ సరళమైన వివరణ కేవలం అవగాహన కోసం మాత్రమే. "
            "మీరు అప్‌లోడ్ చేసిన రిపోర్ట్‌లోని విలువలు మరియు రిఫరెన్స్ పరిధులు మాత్రమే చూపబడ్డాయి; "
            "దయచేసి అన్ని ఫలితాలను మీ డాక్టర్‌తో నిర్ధారించుకోండి."
        ),
        "image": (
            "మెడికల్ ఇమేజ్ పరిమితి గమనిక: AI చూపే పరిశీలనలు కేవలం సమాచారం కోసం మాత్రమే — "
            "ఇవి వైద్య నిర్ధారణ కాదు. దయచేసి అర్హత కలిగిన డాక్టర్ లేదా స్పెషలిస్ట్‌తో పరీక్షించుకోండి."
        ),
        "emergency": (
            "అత్యవసర హెచ్చరిక సంకేతాలు గుర్తించబడ్డాయి: దయచేసి వెంటనే మీ స్థానిక అత్యవసర నంబర్‌కు "
            "(భారతదేశంలో 112 / 108, అమెరికాలో 911) కాల్ చేయండి లేదా సమీపంలోని అత్యవసర ఆసుపత్రికి వెళ్లండి."
        ),
    },
    "hi": {
        "general": (
            "केवल शैक्षिक जानकारी: AI मेडिकल असिस्टेंट कोई चिकित्सीय निदान नहीं करता, "
            "दवाइयाँ नहीं लिखता, और किसी योग्य डॉक्टर की देखभाल का विकल्प नहीं है।"
        ),
        "report": (
            "रिपोर्ट सारांश सूचना: यह सरल व्याख्या केवल सामान्य समझ के लिए है। "
            "इसमें केवल आपकी अपलोड की गई रिपोर्ट के मान और संदर्भ सीमाएँ दिखाई गई हैं; "
            "कृपया सभी परिणाम अपने डॉक्टर से सत्यापित कराएँ।"
        ),
        "image": (
            "मेडिकल इमेज सीमा सूचना: AI द्वारा दिए गए अवलोकन केवल जानकारी के लिए हैं — "
            "यह चिकित्सीय निदान नहीं है। कृपया योग्य डॉक्टर या विशेषज्ञ से जांच कराएँ।"
        ),
        "emergency": (
            "संभावित आपातकालीन चेतावनी संकेत मिले हैं: कृपया तुरंत अपने स्थानीय आपातकालीन नंबर "
            "(भारत में 112 / 108, अमेरिका में 911) पर कॉल करें या नजदीकी इमरजेंसी अस्पताल जाएँ।"
        ),
    },
}


def normalize_language(lang: str | None) -> str:
    code = (lang or "en").strip().lower()
    return code if code in {"en", "te", "hi"} else "en"


def get_disclaimer(kind: str, lang: str | None = "en") -> str:
    code = normalize_language(lang)
    return DISCLAIMERS_BY_LANG[code].get(kind, GENERAL_DISCLAIMER)


_EMERGENCY_PATTERNS: List[Tuple[str, Dict[str, str]]] = [
    (
        r"\bchest\s+pain\b|\bchest\s+tightness\b|\bcrushing\s+chest\b|ఛాతీ\s*నొప్పి|सीने\s*में\s*दर्द|छाती\s*में\s*दर्द",
        {
            "en": "Chest pain or pressure",
            "te": "ఛాతీ నొప్పి లేదా ఒత్తిడి",
            "hi": "सीने में दर्द या दबाव",
        },
    ),
    (
        r"\bshortness\s+of\s+breath\b|\bcan(?:'|no)?t\s+breathe\b|\bdifficulty\s+breathing\b|\btrouble\s+breathing\b|శ్వాస\s*తీసుకోవడంలో\s*ఇబ్బంది|ఊపిరి\s*ఆడకపోవడం|सांस\s*लेने\s*में\s*तकलीफ|सांस\s*फूलना",
        {
            "en": "Severe breathing difficulty",
            "te": "తీవ్రమైన శ్వాస ఇబ్బంది",
            "hi": "सांस लेने में गंभीर कठिनाई",
        },
    ),
    (
        r"\bsuicid(?:e|al)\b|\bkill\s+myself\b|\bself[-\s]?harm\b|\bwant\s+to\s+die\b|ఆత్మహత్య|आत्महत्या|खुद\s*को\s*नुकसान",
        {
            "en": "Mental health crisis / self-harm risk",
            "te": "మానసిక సంక్షోభం / స్వీయ హాని ప్రమాదం",
            "hi": "मानसिक संकट / आत्म-नुकसान का जोखिम",
        },
    ),
    (
        r"\bface\s+drooping\b|\bslurred\s+speech\b|\barm\s+weakness\b|\bsudden\s+numbness\b|\bstroke\b|పక్షవాతం|మాట\s*తడబడటం|लकवा|स्ट्रोक",
        {
            "en": "Possible stroke warning signs",
            "te": "స్ట్రోక్ హెచ్చరిక సంకేతాలు",
            "hi": "स्ट्रोक के संभावित चेतावनी संकेत",
        },
    ),
    (
        r"\bsevere\s+bleeding\b|\buncontrolled\s+bleeding\b|\bcoughing\s+up\s+blood\b|\bvomiting\s+blood\b|తీవ్రమైన\s*రక్తస్రావం|రక్తం\s*వాంతులు|तेज\s*खून\s*बहना|खून\s*की\s*उल्टी",
        {
            "en": "Severe or unusual bleeding",
            "te": "తీవ్రమైన రక్తస్రావం",
            "hi": "गंभीर या असामान्य रक्तस्राव",
        },
    ),
    (
        r"\bunconscious\b|\bpassed\s+out\b|\bfainting\b|\bseizure\b|\bconvulsion\b|స్పృహ\s*కోల్పోవడం|మూర్ఛ|बेहोश|दौरे",
        {
            "en": "Loss of consciousness or seizure",
            "te": "స్పృహ కోల్పోవడం లేదా మూర్ఛ",
            "hi": "बेहोशी या दौरे पड़ना",
        },
    ),
    (
        r"\banaphylaxis\b|\bthroat\s+swelling\b|\btongue\s+swelling\b|\bsevere\s+allergic\s+reaction\b|గొంతు\s*వాపు|गले\s*में\s*सूजन",
        {
            "en": "Possible severe allergic reaction",
            "te": "తీవ్రమైన అలెర్జీ ప్రతిచర్య",
            "hi": "गंभीर एलर्जी प्रतिक्रिया",
        },
    ),
    (
        r"\boverdose\b|\bpoisoning\b|విషప్రయోగం|ओवरडोज़|जहर",
        {
            "en": "Possible overdose or poisoning",
            "te": "అధిక మోతాదు లేదా విషప్రభావం",
            "hi": "ओवरडोज़ या विषाक्तता की संभावना",
        },
    ),
]


def detect_emergency_signals(text: str, lang: str | None = "en") -> Tuple[bool, List[str]]:
    """Inspect user-supplied text for red-flag emergency symptoms in EN/TE/HI."""
    code = normalize_language(lang)
    normalized = (text or "").lower()
    reasons: List[str] = []
    for pattern, labels in _EMERGENCY_PATTERNS:
        if re.search(pattern, normalized):
            reasons.append(labels.get(code, labels["en"]))
    return bool(reasons), reasons
