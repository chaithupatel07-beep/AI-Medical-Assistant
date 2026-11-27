"""Local Ollama detection and built-in educational engines (works with zero API keys)."""

from io import BytesIO
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import httpx
from PIL import Image, ImageFilter, ImageStat

from app.core.safety import get_disclaimer, normalize_language

logger = logging.getLogger("ai_medical_assistant.local_ai")

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")


async def detect_ollama_model(preferred_model: str | None = None) -> Optional[str]:
    """Return a locally running Ollama model name if Ollama is available, else None."""
    if os.environ.get("VERCEL"):
        return None
    try:
        async with httpx.AsyncClient(timeout=0.8) as client:
            res = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if res.status_code != 200:
                return None
            models = [m.get("name") for m in res.json().get("models", []) if m.get("name")]
            if not models:
                return None
            if preferred_model and preferred_model in models:
                return preferred_model
            return models[0]
    except Exception:
        return None


_LAB_GLOSSARY: Dict[str, Dict[str, str]] = {
    "hemoglobin": {
        "en": "Protein in red blood cells that carries oxygen from the lungs throughout the body.",
        "te": "ఊపిరితిత్తుల నుండి శరీర భాగాలకు ఆక్సిజన్‌ను తీసుకెళ్లే ఎర్ర రక్త కణాల ప్రోటీన్.",
        "hi": "लाल रक्त कोशिकाओं का प्रोटीन जो फेफड़ों से पूरे शरीर में ऑक्सीजन पहुंचाता है।",
    },
    "wbc": {
        "en": "White blood cells are part of the immune system and help fight infections.",
        "te": "తెల్ల రక్త కణాలు రోగనిరోధక వ్యవస్థలో భాగం; ఇవి ఇన్ఫెక్షన్లతో పోరాడుతాయి.",
        "hi": "श्वेत रक्त कोशिकाएँ प्रतिरक्षा प्रणाली का हिस्सा हैं जो संक्रमण से लड़ती हैं।",
    },
    "platelets": {
        "en": "Tiny blood cell fragments that help blood clot and stop bleeding.",
        "te": "రక్తం గడ్డకట్టడానికి మరియు రక్తస్రావం ఆపడానికి సహాయపడే చిన్న కణాలు.",
        "hi": "छोटी रक्त कोशिकाएँ जो खून का थक्का जमाने और रक्तस्राव रोकने में मदद करती हैं।",
    },
    "glucose": {
        "en": "Primary blood sugar used by body cells for energy.",
        "te": "శరీర కణాలకు శక్తినిచ్చే రక్తంలోని ప్రధాన చక్కెర.",
        "hi": "शरीर की कोशिकाओं को ऊर्जा देने वाली रक्त शर्करा।",
    },
    "hba1c": {
        "en": "Estimates average blood glucose levels over the past 2 to 3 months.",
        "te": "గత 2 నుండి 3 నెలల సగటు రక్తపు చక్కెర స్థాయిని అంచనా వేస్తుంది.",
        "hi": "पिछले 2 से 3 महीनों के औसत ब्लड शुगर स्तर को दर्शाता है।",
    },
    "cholesterol": {
        "en": "Waxy lipid in blood; evaluated together with HDL, LDL, and triglycerides for heart health.",
        "te": "రక్తంలోని కొవ్వు పదార్థం; గుండె ఆరోగ్యం కోసం HDL, LDL లతో కలిపి చూస్తారు.",
        "hi": "रक्त में मौजूद वसा; हृदय स्वास्थ्य के लिए इसे HDL, LDL के साथ देखा जाता है।",
    },
    "tsh": {
        "en": "Thyroid-stimulating hormone helps regulate metabolism and energy balance.",
        "te": "థైరాయిడ్ గ్రంథి పనితీరు మరియు జీవక్రియను నియంత్రించే హార్మోన్.",
        "hi": "थायरॉइड ग्रंथि के कार्य और चयापचय को नियंत्रित करने वाला हार्मोन।",
    },
    "creatinine": {
        "en": "Waste product filtered by the kidneys, commonly checked to assess kidney function.",
        "te": "కిడ్నీల పనితీరును అంచనా వేయడానికి తనిఖీ చేసే వ్యర్థ పదార్థం.",
        "hi": "किडनी की कार्यक्षमता जांचने के लिए देखा जाने वाला अपशिष्ट पदार्थ।",
    },
    "vitamin d": {
        "en": "Nutrient important for bone strength, calcium absorption, and immune function.",
        "te": "ఎముకల బలం, కాల్షియం శోషణ మరియు రోగనిరోధక శక్తికి ముఖ్యమైన విటమిన్.",
        "hi": "हड्डियों की मजबूती, कैल्शियम अवशोषण और प्रतिरक्षा के लिए आवश्यक विटामिन।",
    },
}

_CHAT_TOPICS: List[Tuple[Tuple[str, ...], Dict[str, str]]] = [
    (
        ("hba1c", "a1c", "diabetes", "blood sugar", "glucose", "షుగర్", "మధుమేహం", "शुगर", "डायबिटीज"),
        {
            "en": (
                "### Understanding Blood Sugar & HbA1c\n\n"
                "- **Fasting Blood Glucose** shows blood sugar at a single moment after fasting.\n"
                "- **Hemoglobin A1c (HbA1c)** estimates your average blood sugar over roughly the past **2 to 3 months**.\n"
                "- **Educational Note**: Diet, fiber intake, physical activity, sleep, and prescribed treatments all affect glucose trends. "
                "Discuss your specific target range with your healthcare provider."
            ),
            "te": (
                "### రక్తంలో చక్కెర & HbA1c అవగాహన\n\n"
                "- **ఫాస్టింగ్ బ్లడ్ షుగర్** ఆ సమయంలో ఉన్న చక్కెర స్థాయిని చూపిస్తుంది.\n"
                "- **HbA1c** గత **2 నుండి 3 నెలల** సగటు రక్తపు చక్కెర స్థాయిని చూపిస్తుంది.\n"
                "- **గమనిక**: ఫైబర్ ఉన్న ఆహారం, నడక మరియు మంచి నిద్ర చక్కెర నియంత్రణకు సహాయపడతాయి. మీ లక్ష్య పరిధిని డాక్టర్‌తో నిర్ధారించుకోండి."
            ),
            "hi": (
                "### ब्लड शुगर और HbA1c की जानकारी\n\n"
                "- **फास्टिंग ब्लड शुगर** किसी एक समय के शुगर स्तर को दिखाता है।\n"
                "- **HbA1c** पिछले **2 से 3 महीनों** के औसत शुगर स्तर को दर्शाता है।\n"
                "- **शैक्षिक नोट**: संतुलित फाइबर आहार, नियमित चलना और अच्छी नींद मदद करते हैं। अपनी लक्ष्य सीमा डॉक्टर से पूछें।"
            ),
        },
    ),
    (
        ("blood pressure", "systolic", "diastolic", "hypertension", "bp", "రక్తపోటు", "బీపీ", "ब्लड प्रेशर", "रक्तचाप"),
        {
            "en": (
                "### Systolic vs. Diastolic Blood Pressure\n\n"
                "- **Systolic (top number)**: Pressure in arteries when your heart beats.\n"
                "- **Diastolic (bottom number)**: Pressure when your heart rests between beats.\n"
                "- **Tip**: Rest quietly for 5 minutes with feet flat before measuring. Seek urgent care if high readings appear with chest pain, severe headache, or shortness of breath."
            ),
            "te": (
                "### సిస్టోలిక్ మరియు డయాస్టోలిక్ రక్తపోటు (BP)\n\n"
                "- **సిస్టోలిక్ (పై సంఖ్య)**: గుండె కొట్టుకునేటప్పుడు రక్తనాళాలపై ఒత్తిడి.\n"
                "- **డయాస్టోలిక్ (కింది సంఖ్య)**: గుండె విశ్రాంతి తీసుకునేటప్పుడు ఉండే ఒత్తిడి.\n"
                "- **సూచన**: బీపీ చూసుకునే ముందు 5 నిమిషాలు ప్రశాంతంగా కూర్చోండి. ఛాతీ నొప్పి లేదా శ్వాస ఇబ్బంది ఉంటే వెంటనే డాక్టర్‌ను కలవండి."
            ),
            "hi": (
                "### सिस्टोलिक और डायस्टोलिक ब्लड प्रेशर\n\n"
                "- **सिस्टोलिक (ऊपर की संख्या)**: हृदय के धड़कने के समय धमनियों में दबाव।\n"
                "- **डायस्टोलिक (नीचे की संख्या)**: धड़कनों के बीच आराम के समय का दबाव।\n"
                "- **सलाह**: मापने से पहले 5 मिनट शांत बैठें। सीने में दर्द या सांस फूलने पर तुरंत चिकित्सा सहायता लें।"
            ),
        },
    ),
    (
        ("cholesterol", "lipid", "ldl", "hdl", "triglycerides", "కొలెస్ట్రాల్", "లిపిడ్", "कोलेस्ट्रॉल", "लिपिड"),
        {
            "en": (
                "### Lipid Panel Basics (LDL, HDL, Triglycerides)\n\n"
                "- **LDL**: Often called 'bad' cholesterol because excess amounts can build up in artery walls.\n"
                "- **HDL**: Often called 'good' cholesterol because it helps clear other forms of cholesterol.\n"
                "- **Triglycerides**: Blood fats influenced by diet, sugars, and physical activity.\n"
                "- Review your full panel and cardiovascular risk with your clinician."
            ),
            "te": (
                "### కొలెస్ట్రాల్ (LDL, HDL, ట్రైగ్లిజరైడ్స్)\n\n"
                "- **LDL**: ఎక్కువైతే రక్తనాళాలలో పేరుకుపోయే కొవ్వు.\n"
                "- **HDL**: అదనపు కొలెస్ట్రాల్‌ను తొలగించడంలో సహాయపడే మంచి కొలెస్ట్రాల్.\n"
                "- **ట్రైగ్లిజరైడ్స్**: ఆహారం మరియు వ్యాయామంపై ఆధారపడే రక్తపు కొవ్వులు. మీ డాక్టర్‌తో ఫలితాలను చర్చించండి."
            ),
            "hi": (
                "### लिपिड प्रोफाइल (LDL, HDL, ट्राइग्लिसराइड्स)\n\n"
                "- **LDL**: अधिक होने पर धमनियों में जम सकता है।\n"
                "- **HDL**: अतिरिक्त कोलेस्ट्रॉल को साफ करने में मदद करता है।\n"
                "- **ट्राइग्लिसराइड्स**: आहार और गतिविधि से प्रभावित होने वाली रक्त वसा। अपने डॉक्टर से पूरा मूल्यांकन कराएँ।"
            ),
        },
    ),
    (
        ("fever", "cough", "cold", "dehydration", "జ్వరం", "దగ్గు", "డీహైడ్రేషన్", "बुखार", "खांसी", "पानी की कमी"),
        {
            "en": (
                "### General Guidance for Fever, Cough, or Dehydration\n\n"
                "- **Hydration & Rest**: Sip water or oral rehydration fluids regularly and get adequate rest.\n"
                "- **Dehydration Signs**: Very dark urine, dizziness when standing, dry mouth, or inability to keep fluids down.\n"
                "- **When to See a Doctor**: Persistent high fever, breathing difficulty, chest pain, confusion, or symptoms worsening after several days."
            ),
            "te": (
                "### జ్వరం, దగ్గు లేదా నీటి కొరతపై సాధారణ సూచనలు\n\n"
                "- **విశ్రాంతి & ద్రవాలు**: తరచుగా నీరు లేదా ORS తీసుకోండి మరియు తగినంత విశ్రాంతి తీసుకోండి.\n"
                "- **డీహైడ్రేషన్ సంకేతాలు**: మూత్రం చాలా తగ్గడం, కళ్లు తిరగడం, నోరు ఎండిపోవడం.\n"
                "- **డాక్టర్‌ను ఎప్పుడు కలవాలి**: అధిక జ్వరం తగ్గకపోయినా, శ్వాస ఇబ్బంది ఉన్నా వెంటనే డాక్టర్‌ను సంప్రదించండి."
            ),
            "hi": (
                "### बुखार, खांसी या पानी की कमी की सामान्य जानकारी\n\n"
                "- **आराम और तरल पदार्थ**: नियमित रूप से पानी या ORS पिएँ और आराम करें।\n"
                "- **डीहाइड्रेशन के संकेत**: गहरे रंग का पेशाब, चक्कर आना, मुंह सूखना।\n"
                "- **डॉक्टर को कब दिखाएँ**: लगातार तेज बुखार, सांस की तकलीफ या कई दिनों तक लक्षण बढ़ने पर तुरंत डॉक्टर से मिलें।"
            ),
        },
    ),
    (
        ("doctor", "visit", "prepare", "questions", "డాక్టర్", "ప్రశ్నలు", "डॉक्टर", "सवाल"),
        {
            "en": (
                "### Preparing for Your Doctor Appointment\n\n"
                "1. List your main symptoms, when they started, and what makes them better or worse.\n"
                "2. Bring your current medications, supplements, and recent lab reports.\n"
                "3. Ask: *What could explain these symptoms? Which tests are helpful? What warning signs mean I should seek urgent care?*"
            ),
            "te": (
                "### డాక్టర్ భేటీకి ముందు సిద్ధం చేసుకోవాల్సినవి\n\n"
                "1. మీ లక్షణాలు ఎప్పుడు మొదలయ్యాయో, తీవ్రత ఎలా ఉందో నోట్ చేసుకోండి.\n"
                "2. ప్రస్తుతం వాడుతున్న మందులు మరియు పాత రిపోర్టులను తీసుకెళ్లండి.\n"
                "3. డాక్టర్‌ను అడగండి: *దీనికి సాధారణ కారణాలు ఏమిటి? ఏ పరీక్షలు అవసరం? ఏ హెచ్చరిక సంకేతాలు వస్తే వెంటనే రావాలి?*"
            ),
            "hi": (
                "### डॉक्टर से मिलने की तैयारी कैसे करें\n\n"
                "1. अपने लक्षण, उनकी शुरुआत और गंभीरता लिखकर ले जाएँ।\n"
                "2. वर्तमान दवाइयों की सूची और पुरानी रिपोर्ट साथ रखें।\n"
                "3. पूछें: *संभावित कारण क्या हो सकते हैं? कौन-सी जांच जरूरी है? किन चेतावनी संकेतों पर तुरंत आना चाहिए?*"
            ),
        },
    ),
]


def generate_rule_based_chat_reply(
    user_message: str,
    emergency_detected: bool,
    language: str = "en",
) -> Tuple[str, str]:
    """Built-in offline educational healthcare response engine (clearly non-generative)."""
    lang = normalize_language(language)
    lower = (user_message or "").lower()
    header = {
        "en": "_Mode: Built-in Educational Engine (Offline — No API Key Required)_\n\n",
        "te": "_మోడ్: అంతర్నిర్మిత విద్యా ఇంజిన్ (ఆఫ్‌లైన్ — API కీ అవసరం లేదు)_\n\n",
        "hi": "_मोड: अंतर्निर्मित शैक्षिक इंजन (ऑफ़लाइन — API कुंजी की आवश्यकता नहीं)_\n\n",
    }[lang]

    body = ""
    for keywords, replies in _CHAT_TOPICS:
        if any(kw in lower for kw in keywords):
            body = replies[lang]
            break

    if not body:
        body = {
            "en": (
                "### General Health Education Guidance\n\n"
                "I am running in **Built-in Educational Engine** mode (no external AI API key configured). "
                "I can explain common medical terms (like **HbA1c**, **blood pressure**, **cholesterol/lipids**, **CBC/hemoglobin**, **TSH**), "
                "fever/dehydration warning signs, and doctor-visit preparation.\n\n"
                "- **Safety Reminder**: For personalized medical questions, diagnosis, or treatment, please consult a licensed healthcare professional."
            ),
            "te": (
                "### సాధారణ ఆరోగ్య అవగాహన సూచన\n\n"
                "ప్రస్తుతం **అంతర్నిర్మిత విద్యా ఇంజిన్** మోడ్ నడుస్తోంది (API కీ అవసరం లేదు). "
                "మీరు **HbA1c**, **రక్తపోటు (BP)**, **కొలెస్ట్రాల్**, **జ్వరం/డీహైడ్రేషన్**, లేదా **డాక్టర్ భేటీ ప్రశ్నలు** గురించి అడగవచ్చు.\n\n"
                "- **భద్రతా గమనిక**: వ్యక్తిగత వైద్య నిర్ధారణ లేదా చికిత్స కోసం దయచేసి అర్హత కలిగిన డాక్టర్‌ను సంప్రదించండి."
            ),
            "hi": (
                "### सामान्य स्वास्थ्य शिक्षा मार्गदर्शन\n\n"
                "यह **अंतर्निर्मित शैक्षिक इंजन** मोड में चल रहा है (किसी बाहरी API कुंजी की आवश्यकता नहीं है)। "
                "आप **HbA1c**, **ब्लड प्रेशर**, **कोलेस्ट्रॉल**, **बुखार/डीहाइड्रेशन**, या **डॉक्टर से पूछने योग्य प्रश्नों** के बारे में पूछ सकते हैं।\n\n"
                "- **सुरक्षा सूचना**: व्यक्तिगत निदान या उपचार के लिए कृपया योग्य डॉक्टर से परामर्श लें।"
            ),
        }[lang]

    if emergency_detected:
        body = f"**{get_disclaimer('emergency', lang)}**\n\n{body}"

    return f"{header}{body}\n\n> {get_disclaimer('general', lang)}", "built-in-educational-engine"


def generate_rule_based_symptom_guidance(
    payload: Dict[str, Any],
    emergency_detected: bool,
    emergency_reasons: List[str],
    language: str = "en",
) -> Tuple[Dict[str, Any], str]:
    """Transparent local educational symptom rules engine (non-diagnostic)."""
    lang = normalize_language(language)
    symptom = str(payload.get("main_symptom", "")).strip()
    severity = str(payload.get("severity", "mild")).lower()
    severity_score = payload.get("severity_score")
    severity_display = f"{severity} ({severity_score}/10)" if severity_score else severity
    duration = str(payload.get("duration", "")).strip()
    age = payload.get("age")

    text_map = {
        "en": {
            "overview": (
                f"Educational summary (Offline Rules Engine, aligned with MedlinePlus/CDC/WHO guidance) for age {age} reporting '{symptom}' "
                f"({severity_display} severity, duration: {duration}). This is general educational context, not a medical diagnosis."
            ),
            "exp1_t": "Common self-limiting or lifestyle-related contributors (possibility)",
            "exp1_d": "Everyday factors such as viral exposure, fatigue, dehydration, muscle strain, or sleep disruption commonly contribute to mild-to-moderate symptoms.",
            "exp2_t": "Underlying inflammatory, allergic, or chronic factor (possibility)",
            "exp2_d": "Persistent or recurring symptoms can sometimes reflect allergies, localized irritation, or an underlying condition best evaluated by a clinician.",
            "steps": [
                "Track symptom timing, temperature (if applicable), and any triggers in a brief log.",
                "Stay hydrated with water or oral rehydration fluids and prioritize rest.",
                "Avoid taking unprescribed antibiotics or leftover prescription medicines.",
            ],
            "warnings": [
                "Difficulty breathing, chest pain/pressure, or bluish lips",
                "Confusion, fainting, sudden weakness, or slurred speech",
                "Persistent high fever or inability to keep fluids down",
            ],
            "when": (
                "Seek prompt or urgent medical attention if symptoms are severe, worsening, "
                "or persist beyond a few days without improvement."
            ),
            "questions": [
                "What are the most likely non-serious vs. concerning explanations for these symptoms?",
                "Are any basic exams or lab tests recommended?",
                "Which warning signs mean I should return for urgent care?",
            ],
        },
        "te": {
            "overview": (
                f"వయస్సు {age}, లక్షణం '{symptom}' ({severity}, కాలం: {duration}) కోసం ఆఫ్‌లైన్ విద్యా సమాచారం. "
                "ఇది కేవలం సాధారణ అవగాహన మాత్రమే — వైద్య నిర్ధారణ కాదు."
            ),
            "exp1_t": "సాధారణ వైరల్, అలసట లేదా జీవనశైలి కారణాలు (అవకాశం మాత్రమే)",
            "exp1_d": "తేలికపాటి జలుబు/వైరల్ ఇన్ఫెక్షన్, నీటి కొరత, నిద్రలేమి లేదా కండరాల అలసట వంటి సాధారణ అంశాలు కారణం కావచ్చు.",
            "exp2_t": "అలెర్జీ లేదా కొనసాగే ఆరోగ్య కారణం (అవకాశం మాత్రమే)",
            "exp2_d": "లక్షణాలు తగ్గకుండా కొనసాగితే అలెర్జీ లేదా ఇతర వైద్య కారణాల కోసం డాక్టర్ పరీక్ష అవసరం కావచ్చు.",
            "steps": [
                "లక్షణాలు ఎప్పుడు పెరుగుతున్నాయి/తగ్గుతున్నాయి అని రాసుకోండి.",
                "తగినంత నీరు త్రాగండి మరియు విశ్రాంతి తీసుకోండి.",
                "డాక్టర్ సలహా లేకుండా పాత లేదా యాంటీబయాటిక్ మందులు వాడకండి.",
            ],
            "warnings": [
                "శ్వాస తీసుకోవడంలో ఇబ్బంది లేదా ఛాతీ నొప్పి",
                "స్పృహ తప్పడం, గందరగోళం లేదా ఆకస్మిక బలహీనత",
                "తగ్గని అధిక జ్వరం లేదా నీరు నిలబడకపోవడం",
            ],
            "when": "లక్షణాలు తీవ్రంగా ఉన్నా, రోజురోజుకు పెరుగుతున్నా లేదా కొన్ని రోజులుగా తగ్గకపోతే వెంటనే డాక్టర్‌ను కలవండి.",
            "questions": [
                "ఈ లక్షణాలకు సాధారణ కారణాలు ఏమిటి?",
                "ఏదైనా రక్త పరీక్ష లేదా ఇతర పరీక్ష అవసరమా?",
                "ఏ హెచ్చరిక సంకేతాలు కనిపిస్తే అత్యవసరంగా రావాలి?",
            ],
        },
        "hi": {
            "overview": (
                f"आयु {age}, मुख्य लक्षण '{symptom}' ({severity}, अवधि: {duration}) के लिए ऑफ़लाइन शैक्षिक सारांश। "
                "यह केवल सामान्य जानकारी है — चिकित्सीय निदान नहीं।"
            ),
            "exp1_t": "सामान्य वायरल, थकान या जीवनशैली से जुड़े कारण (संभावना मात्र)",
            "exp1_d": "हल्का वायरल संक्रमण, पानी की कमी, नींद की कमी या तनाव अक्सर ऐसे लक्षणों में योगदान देते हैं।",
            "exp2_t": "एलर्जी या लगातार चलने वाला कारण (संभावना मात्र)",
            "exp2_d": "यदि लक्षण लगातार बने रहें तो एलर्जी या अन्य कारणों की जांच डॉक्टर द्वारा आवश्यक हो सकती है।",
            "steps": [
                "लक्षणों के समय, बुखार और बदलावों का संक्षिप्त रिकॉर्ड रखें।",
                "पर्याप्त पानी/तरल पदार्थ लें और आराम करें।",
                "बिना डॉक्टर की सलाह के एंटीबायोटिक्स या पुरानी दवाइयाँ न लें।",
            ],
            "warnings": [
                "सांस लेने में कठिनाई या सीने में दर्द/दबाव",
                "चक्कर आना, बेहोशी, भ्रम या अचानक कमजोरी",
                "लगातार तेज बुखार या तरल पदार्थ न टिक पाना",
            ],
            "when": "यदि लक्षण गंभीर हों, बढ़ रहे हों या कुछ दिनों में ठीक न हों तो तुरंत डॉक्टर से परामर्श लें।",
            "questions": [
                "इन लक्षणों के सामान्य संभावित कारण क्या हो सकते हैं?",
                "क्या कोई बुनियादी जांच या लैब टेस्ट जरूरी है?",
                "किन चेतावनी संकेतों पर मुझे तुरंत अस्पताल आना चाहिए?",
            ],
        },
    }[lang]

    result: Dict[str, Any] = {
        "educational_overview": text_map["overview"],
        "possible_explanations": [
            {"title": text_map["exp1_t"], "description": text_map["exp1_d"]},
            {"title": text_map["exp2_t"], "description": text_map["exp2_d"]},
        ],
        "recommended_next_steps": text_map["steps"],
        "warning_signs": text_map["warnings"],
        "when_to_consult_doctor": text_map["when"],
        "questions_for_doctor": text_map["questions"],
        "questions_for_doctor_en": [
            "What are the most likely non-serious vs. concerning explanations for these symptoms?",
            "Are any basic exams or lab tests recommended?",
            "Which warning signs mean I should return for urgent care?",
        ],
        "severity_score": severity_score,
        "emergency_detected": emergency_detected,
        "emergency_reasons": emergency_reasons,
        "disclaimer": get_disclaimer("general", lang),
    }
    if emergency_detected:
        result["emergency_banner"] = get_disclaimer("emergency", lang)
    return result, "built-in-rules-engine"


def generate_rule_based_report_summary(
    extracted_text: str,
    deterministic_markers: List[Dict[str, Any]],
    language: str = "en",
) -> Tuple[Dict[str, Any], str]:
    """Deterministic local medical report summarizer using extracted text & markers only."""
    lang = normalize_language(language)
    enriched_markers = []
    terms = []
    seen_terms = set()

    for m in deterministic_markers:
        name = str(m.get("name", ""))
        lower_name = name.lower()
        explanation = ""
        for key, gloss in _LAB_GLOSSARY.items():
            if key in lower_name:
                explanation = gloss[lang]
                if key not in seen_terms:
                    seen_terms.add(key)
                    terms.append({"term": name, "simple_explanation": explanation})
                break
        enriched_markers.append(
            {
                "name": name,
                "value": str(m.get("value", "")),
                "unit": str(m.get("unit", "")),
                "reference_range": str(m.get("reference_range", "Not specified in report")),
                "status": str(m.get("status", "unknown")),
                "explanation": explanation,
            }
        )

    high_count = sum(1 for m in enriched_markers if m["status"] == "high")
    low_count = sum(1 for m in enriched_markers if m["status"] == "low")
    total_count = len(enriched_markers)

    summary_map = {
        "en": (
            f"Local Deterministic Report Summary: Extracted {len(extracted_text)} characters and identified "
            f"{total_count} laboratory marker(s) directly from the document ({high_count} high, {low_count} low "
            f"based strictly on reference ranges printed in the report). No external reference ranges were invented."
        ),
        "te": (
            f"స్థానిక రిపోర్ట్ సారాంశం: డాక్యుమెంట్ నుండి {len(extracted_text)} అక్షరాలు మరియు {total_count} ల్యాబ్ విలువలు గుర్తించబడ్డాయి "
            f"(రిపోర్ట్‌లో ఉన్న రిఫరెన్స్ పరిధుల ప్రకారం {high_count} ఎక్కువ, {low_count} తక్కువ). ఎలాంటి విలువలు ఊహించి చేర్చబడలేదు."
        ),
        "hi": (
            f"स्थानीय रिपोर्ट सारांश: दस्तावेज़ से {len(extracted_text)} अक्षर और {total_count} लैब मान निकाले गए "
            f"(केवल रिपोर्ट में छपी संदर्भ सीमाओं के अनुसार {high_count} उच्च, {low_count} निम्न)। कोई भी मान काल्पनिक रूप से नहीं जोड़ा गया है।"
        ),
    }[lang]

    questions_map = {
        "en": [
            "How do these results compare with my previous laboratory values?",
            "Do any out-of-range or borderline values require follow-up testing?",
        ],
        "te": [
            "ఈ ఫలితాలు నా గత ల్యాబ్ రిపోర్టులతో ఎలా పోల్చబడతాయి?",
            "పరిధికి మించిన విలువల కోసం తదుపరి పరీక్షలు అవసరమా?",
        ],
        "hi": [
            "ये परिणाम मेरी पिछली लैब रिपोर्ट की तुलना में कैसे हैं?",
            "क्या किसी सीमा से बाहर के मान के लिए दोबारा जांच की आवश्यकता है?",
        ],
    }[lang]

    warnings_map = {
        "en": [
            "Generated by local deterministic parser (no external generative AI key configured).",
            "Always confirm interpretation with your ordering physician.",
        ],
        "te": [
            "స్థానిక పార్సర్ ద్వారా తయారు చేయబడింది (బాహ్య AI కీ అవసరం లేదు).",
            "దయచేసి ఎల్లప్పుడూ మీ డాక్టర్‌తో ఫలితాలను నిర్ధారించుకోండి.",
        ],
        "hi": [
            "स्थानीय पार्सर द्वारा तैयार (कोई बाहरी AI कुंजी आवश्यक नहीं)।",
            "कृपया हमेशा अपने डॉक्टर से परिणामों की पुष्टि कराएँ।",
        ],
    }[lang]

    return {
        "plain_summary": summary_map,
        "lab_markers": enriched_markers,
        "medical_terms": terms,
        "questions_for_doctor": questions_map,
        "warnings": warnings_map,
        "disclaimer": get_disclaimer("report", lang),
    }, "local-deterministic-parser"


def analyze_image_locally(
    raw_bytes: bytes,
    mime_type: str,
    image_context: str | None,
    language: str = "en",
) -> Tuple[Dict[str, Any], str]:
    """Local Pillow metadata & basic image quality check (non-diagnostic)."""
    lang = normalize_language(language)
    with Image.open(BytesIO(raw_bytes)) as img:
        width, height = img.size
        mode = img.mode
        fmt = img.format or mime_type
        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        mean_brightness = round(stat.mean[0], 1)
        contrast_std = round(stat.stddev[0], 1)
        edge_stat = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES))
        sharpness_score = round(edge_stat.mean[0], 1)

    quality_notes = []
    if width < 300 or height < 300:
        quality_notes.append("Low resolution (<300px) — fine details may be unclear.")
    if mean_brightness < 45:
        quality_notes.append("Image appears quite dark.")
    elif mean_brightness > 225:
        quality_notes.append("Image appears overexposed/bright.")
    if sharpness_score < 6:
        quality_notes.append("Image appears soft or slightly blurred.")

    ctx_note = f" Context provided: {image_context}." if image_context else ""

    msg_map = {
        "en": {
            "summary": (
                f"Local Image Inspection Complete ({fmt}, {width}x{height}px, mode {mode}).{ctx_note} "
                "No clinical or medical vision model is active, so clinical image interpretation is unavailable."
            ),
            "obs": [
                f"Dimensions & Format: {width} × {height} px ({fmt}, {mode})",
                f"Estimated Brightness: {mean_brightness}/255 | Contrast (StdDev): {contrast_std} | Edge Sharpness: {sharpness_score}",
                *(quality_notes or ["Image resolution and lighting appear adequate for basic viewing."]),
            ],
            "limits": (
                "Clinical image interpretation is unavailable in offline local mode because no medical vision model is installed. "
                "Pixel statistics cannot detect medical conditions and must never be treated as diagnostic findings."
            ),
            "next": "Please share the original image directly with a qualified physician, dermatologist, or radiologist for clinical evaluation.",
        },
        "te": {
            "summary": (
                f"స్థానిక చిత్ర తనిఖీ పూర్తయింది ({fmt}, {width}x{height}px).{ctx_note} "
                "వైద్య విజన్ మోడల్ ఇన్‌స్టాల్ కానందున క్లినికల్ విశ్లేషణ అందుబాటులో లేదు."
            ),
            "obs": [
                f"కొలతలు & ఫార్మాట్: {width} × {height} px ({fmt}, {mode})",
                f"ప్రకాశం (Brightness): {mean_brightness}/255 | స్పష్టత (Sharpness): {sharpness_score}",
            ],
            "limits": (
                "ఆఫ్‌లైన్ మోడ్‌లో వైద్య చిత్ర నిర్ధారణ అందుబాటులో లేదు. ఇవి కేవలం చిత్ర నాణ్యత కొలతలు మాత్రమే — వ్యాధి నిర్ధారణ కాదు."
            ),
            "next": "దయచేసి అసలు చిత్రాన్ని అర్హత కలిగిన డాక్టర్ లేదా స్పెషలిస్ట్‌కు చూపించండి.",
        },
        "hi": {
            "summary": (
                f"स्थानीय छवि जांच पूर्ण ({fmt}, {width}x{height}px)।{ctx_note} "
                "कोई चिकित्सीय विज़न मॉडल सक्रिय नहीं है, इसलिए नैदानिक व्याख्या उपलब्ध नहीं है।"
            ),
            "obs": [
                f"आकार और प्रारूप: {width} × {height} px ({fmt}, {mode})",
                f"चमक (Brightness): {mean_brightness}/255 | स्पष्टता (Sharpness): {sharpness_score}",
            ],
            "limits": (
                "ऑफ़लाइन मोड में चिकित्सीय छवि विश्लेषण उपलब्ध नहीं है। ये केवल तकनीकी छवि गुणवत्ता आँकड़े हैं — निदान नहीं।"
            ),
            "next": "कृपया सटीक जांच के लिए मूल छवि योग्य डॉक्टर या विशेषज्ञ को दिखाएँ।",
        },
    }[lang]

    return {
        "analysis_summary": msg_map["summary"],
        "observations": msg_map["obs"],
        "limitations": msg_map["limits"],
        "recommended_next_steps": msg_map["next"],
        "disclaimer": get_disclaimer("image", lang),
    }, "local-pillow-inspector"
