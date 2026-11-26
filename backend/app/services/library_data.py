"""Curated health education articles across 6 categories in English, Telugu, and Hindi."""

from typing import Any, Dict, List

CATEGORIES: List[str] = [
    "General Health",
    "Nutrition",
    "Fitness and Exercise",
    "Preventive Healthcare",
    "Common Health Conditions",
    "Mental Wellness",
]

CATEGORY_LABELS: Dict[str, Dict[str, str]] = {
    "General Health": {"en": "General Health", "te": "సాధారణ ఆరోగ్యం", "hi": "सामान्य स्वास्थ्य"},
    "Nutrition": {"en": "Nutrition", "te": "పోషకాహారం", "hi": "पोषण"},
    "Fitness and Exercise": {"en": "Fitness and Exercise", "te": "ఫిట్‌నెస్ & వ్యాయామం", "hi": "फिटनेस और व्यायाम"},
    "Preventive Healthcare": {"en": "Preventive Healthcare", "te": "నివారణ ఆరోగ్య సంరక్షణ", "hi": "निवारक स्वास्थ्य देखभाल"},
    "Common Health Conditions": {"en": "Common Health Conditions", "te": "సాధారణ ఆరోగ్య సమస్యలు", "hi": "सामान्य स्वास्थ्य समस्याएँ"},
    "Mental Wellness": {"en": "Mental Wellness", "te": "మానసిక ఆరోగ్యం", "hi": "मानसिक स्वास्थ्य"},
}

READ_TIME_LABEL = {"en": "min read", "te": "నిమిషాల చదువు", "hi": "मिनट पढ़ें"}

ARTICLES: List[Dict[str, Any]] = [
    {
        "id": "gen-understanding-lab-tests",
        "category": "General Health",
        "read_minutes": 5,
        "source_name": "MedlinePlus (NIH)",
        "source_url": "https://medlineplus.gov/lab-tests/",
        "translations": {
            "en": {
                "title": "Understanding Common Blood Tests and Reference Ranges",
                "summary": "Learn what a Complete Blood Count (CBC) and Basic Metabolic Panel (BMP) measure and why reference ranges vary by lab.",
                "content": (
                    "Routine blood panels help clinicians evaluate organ function, hydration, electrolyte balance, and blood cell counts. "
                    "A reference range represents the typical values seen in a healthy population, though individual baselines, age, sex, and "
                    "laboratory methods all influence interpretation.\n\n"
                    "Slightly out-of-range numbers do not automatically mean illness—hydration, recent meals, exercise, or medications can shift results. "
                    "Always review laboratory reports alongside your clinician."
                ),
                "key_takeaways": [
                    "Reference ranges differ slightly between laboratories based on testing equipment.",
                    "A single borderline result is often interpreted alongside trends over time.",
                    "Bring a list of supplements and medications when discussing lab results.",
                ],
                "when_to_see_doctor": "Contact your healthcare provider promptly if a report flags critical values or if you experience new or worsening symptoms.",
            },
            "te": {
                "title": "సాధారణ రక్త పరీక్షలు మరియు రిఫరెన్స్ పరిధులను అర్థం చేసుకోవడం",
                "summary": "CBC మరియు BMP వంటి రక్త పరీక్షలు ఏమి కొలుస్తాయో మరియు ల్యాబ్ రిఫరెన్స్ విలువలు ఎందుకు మారుతాయో తెలుసుకోండి.",
                "content": (
                    "సాధారణ రక్త పరీక్షలు డాక్టర్లకు అవయవాల పనితీరు, శరీరంలో నీటి స్థాయి, ఎలక్ట్రోలైట్ సమతుల్యత మరియు రక్త కణాల సంఖ్యను తెలుసుకోవడానికి సహాయపడతాయి. "
                    "రిఫరెన్స్ రేంజ్ అనేది ఆరోగ్యవంతమైన వ్యక్తులలో కనిపించే సాధారణ విలువల పరిధిని సూచిస్తుంది.\n\n"
                    "ఒక విలువ కొద్దిగా ఎక్కువ లేదా తక్కువగా ఉన్నంత మాత్రాన వెంటనే అనారోగ్యం ఉందని కాదు—భోజనం, నీరు త్రాగడం, వ్యాయామం లేదా మందులు ఫలితాలను ప్రభావితం చేయవచ్చు. "
                    "మీ రిపోర్ట్‌ను ఎల్లప్పుడూ డాక్టర్‌తో కలిపి సమీక్షించండి."
                ),
                "key_takeaways": [
                    "ల్యాబ్ పరికరాల ఆధారంగా రిఫరెన్స్ పరిధులు కొద్దిగా మారవచ్చు.",
                    "ఒకే ఫలితం కంటే కాలక్రమేణా వచ్చే మార్పులను డాక్టర్లు పరిశీలిస్తారు.",
                    "ల్యాబ్ రిపోర్ట్ చూపించేటప్పుడు మీరు వాడే మందులు మరియు సప్లిమెంట్ల వివరాలు తీసుకువెళ్లండి.",
                ],
                "when_to_see_doctor": "రిపోర్ట్‌లో క్రిటికల్ విలువలు ఉన్నా లేదా కొత్త లక్షణాలు పెరుగుతున్నా వెంటనే డాక్టర్‌ను సంప్రదించండి.",
            },
            "hi": {
                "title": "सामान्य रक्त जांच और रेफरेंस रेंज को समझना",
                "summary": "जानें कि CBC और BMP जैसी रक्त जांच क्या मापती हैं और विभिन्न लैब में रेफरेंस रेंज क्यों बदलती है।",
                "content": (
                    "नियमित रक्त जांच डॉक्टरों को अंगों के कार्य, शरीर में पानी के स्तर, इलेक्ट्रोलाइट संतुलन और रक्त कोशिकाओं की संख्या समझने में मदद करती है। "
                    "रेफरेंस रेंज स्वस्थ लोगों में देखे जाने वाले सामान्य मानों को दर्शाती है।\n\n"
                    "यदि कोई मान थोड़ा ऊपर या नीचे है तो इसका मतलब हमेशा बीमारी नहीं होता—भोजन, पानी की कमी, व्यायाम या दवाइयाँ भी परिणाम बदल सकती हैं। "
                    "अपनी लैब रिपोर्ट हमेशा डॉक्टर की सलाह के साथ ही समझें।"
                ),
                "key_takeaways": [
                    "लैब की मशीन और तकनीक के अनुसार रेफरेंस रेंज थोड़ा भिन्न हो सकती है।",
                    "एक बार के सीमांत परिणाम की तुलना पिछले रुझानों से की जाती है।",
                    "डॉक्टर से बात करते समय अपनी दवाइयों और सप्लीमेंट्स की सूची साथ रखें।",
                ],
                "when_to_see_doctor": "यदि रिपोर्ट में गंभीर मान दिखें या नए लक्षण बढ़ें तो तुरंत अपने डॉक्टर से संपर्क करें।",
            },
        },
    },
    {
        "id": "gen-sleep-hygiene",
        "category": "General Health",
        "read_minutes": 4,
        "source_name": "CDC Sleep Health",
        "source_url": "https://www.cdc.gov/sleep/about/index.html",
        "translations": {
            "en": {
                "title": "Healthy Sleep Habits for Immune and Cardiovascular Support",
                "summary": "Why consistent sleep schedules matter for energy, focus, blood pressure regulation, and metabolic health.",
                "content": (
                    "Most adults need 7 to 9 hours of quality sleep per night. Consistent sleep and wake times help regulate circadian rhythms, "
                    "hormone balance, and tissue repair.\n\n"
                    "Helpful habits include keeping your bedroom cool and dark, limiting caffeine in the afternoon, and stepping away from bright screens "
                    "30–60 minutes before bed."
                ),
                "key_takeaways": [
                    "Aim for 7–9 hours of sleep on a consistent daily schedule.",
                    "Limit caffeine within 8 hours of bedtime.",
                    "Morning daylight exposure helps anchor your natural sleep-wake cycle.",
                ],
                "when_to_see_doctor": "Speak with a clinician if you experience loud snoring with gasping, persistent insomnia, or severe daytime sleepiness.",
            },
            "te": {
                "title": "రోగనిరోధక శక్తి మరియు గుండె ఆరోగ్యం కోసం మంచి నిద్ర అలవాట్లు",
                "summary": "రోజూ ఒకే సమయానికి నిద్రపోవడం శక్తి, ఏకాగ్రత మరియు రక్తపోటు నియంత్రణకు ఎందుకు ముఖ్యమో తెలుసుకోండి.",
                "content": (
                    "చాలా మంది పెద్దలకు రాత్రికి 7 నుండి 9 గంటల నాణ్యమైన నిద్ర అవసరం. ప్రతిరోజూ ఒకే సమయానికి నిద్రపోయి మేల్కొనడం శరీర జీవ గడియారాన్ని (circadian rhythm) సమతుల్యంగా ఉంచుతుంది.\n\n"
                    "పడుకునే గదిని చల్లగా మరియు చీకటిగా ఉంచడం, మధ్యాహ్నం తర్వాత కెఫీన్ తగ్గించడం, మరియు నిద్రకు 30–60 నిమిషాల ముందు ఫోన్/టీవీ స్క్రీన్లను ఆపడం ఎంతో ఉపయోగపడుతుంది."
                ),
                "key_takeaways": [
                    "రోజూ 7–9 గంటల నిద్ర కోసం ప్రయత్నించండి.",
                    "నిద్రకు 8 గంటల ముందు కాఫీ/టీ తగ్గించండి.",
                    "ఉదయం సూర్యకాంతి శరీర నిద్ర చక్రాన్ని సరిచేస్తుంది.",
                ],
                "when_to_see_doctor": "తీవ్రమైన గురక, నిద్రలో శ్వాస ఆగిపోవడం, లేదా దీర్ఘకాలిక నిద్రలేమి ఉంటే డాక్టర్‌ను కలవండి.",
            },
            "hi": {
                "title": "प्रतिरक्षा और हृदय स्वास्थ्य के लिए अच्छी नींद की आदतें",
                "summary": "ऊर्जा, एकाग्रता और ब्लड प्रेशर संतुलन के लिए नियमित नींद का समय क्यों ज़रूरी है।",
                "content": (
                    "अधिकांश वयस्कों को हर रात 7 से 9 घंटे की अच्छी नींद की आवश्यकता होती है। रोज़ एक ही समय पर सोने और जागने से शरीर की जैविक घड़ी और हार्मोन संतुलित रहते हैं।\n\n"
                    "कमरे को ठंडा और अंधेरा रखना, दोपहर के बाद कैफीन सीमित करना, और सोने से 30–60 मिनट पहले मोबाइल या टीवी स्क्रीन से दूर रहना लाभदायक होता है।"
                ),
                "key_takeaways": [
                    "रोज़ाना 7–9 घंटे की नियमित नींद लेने का लक्ष्य रखें।",
                    "सोने से 8 घंटे पहले चाय या कॉफी कम करें।",
                    "सुबह की धूप प्राकृतिक नींद चक्र को बेहतर बनाती है।",
                ],
                "when_to_see_doctor": "तेज़ खर्राटे, नींद में सांस रुकना, या लगातार अनिद्रा हो तो डॉक्टर से सलाह लें।",
            },
        },
    },
    {
        "id": "nut-balanced-plate",
        "category": "Nutrition",
        "read_minutes": 5,
        "source_name": "WHO Healthy Diet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
        "translations": {
            "en": {
                "title": "Building a Balanced, Heart-Friendly Daily Diet",
                "summary": "Practical evidence-based guidance on fiber, whole grains, lean proteins, healthy fats, and sodium awareness.",
                "content": (
                    "A balanced eating pattern emphasizes vegetables, fruits, whole grains, legumes, nuts, and lean protein sources while limiting added sugars, "
                    "excess sodium, and trans fats.\n\n"
                    "Dietary fiber supports digestive regularity, steadier blood glucose responses, and healthy cholesterol levels."
                ),
                "key_takeaways": [
                    "Fill half your plate with colorful non-starchy vegetables and fruits.",
                    "Choose unsaturated fats (olive oil, nuts, fatty fish) over saturated fats.",
                    "Limit sodium intake and ultra-processed foods to support blood pressure.",
                ],
                "when_to_see_doctor": "Consult a doctor or registered dietitian before making major dietary changes if you have kidney disease, diabetes, or food allergies.",
            },
            "te": {
                "title": "గుండె ఆరోగ్యానికి సమతుల్య రోజువారీ ఆహారం",
                "summary": "ఫైబర్, తృణధాన్యాలు, ప్రోటీన్లు, మంచి కొవ్వులు మరియు ఉప్పు నియంత్రణపై ఆధారపడిన ఆహార సూచనలు.",
                "content": (
                    "సమతుల్య ఆహారంలో తాజా కూరగాయలు, పండ్లు, తృణధాన్యాలు, పప్పులు, గింజలు మరియు మంచి ప్రోటీన్లు ఉండాలి. అదనపు చక్కెర, ఎక్కువ ఉప్పు మరియు ట్రాన్స్ ఫ్యాట్లను తగ్గించాలి.\n\n"
                    "ఆహారంలోని ఫైబర్ జీర్ణక్రియను మెరుగుపరుస్తుంది, రక్తంలో చక్కెర స్థాయిలను స్థిరంగా ఉంచుతుంది మరియు కొలెస్ట్రాల్ నియంత్రణకు సహాయపడుతుంది."
                ),
                "key_takeaways": [
                    "మీ ప్లేట్‌లో సగం భాగం కూరగాయలు మరియు పండ్లతో నింపండి.",
                    "ఆలివ్ ఆయిల్, బాదం, చేపలు వంటి ఆరోగ్యకరమైన కొవ్వులను ఎంచుకోండి.",
                    "అధిక ఉప్పు మరియు ప్రాసెస్డ్ ఆహారాలను తగ్గించండి.",
                ],
                "when_to_see_doctor": "మీకు మధుమేహం, కిడ్నీ సమస్యలు లేదా ఆహార అలెర్జీలు ఉంటే డైట్ మార్పుల ముందు డాక్టర్ లేదా డైటీషియన్‌ను సంప్రదించండి.",
            },
            "hi": {
                "title": "हृदय के अनुकूल संतुलित दैनिक आहार",
                "summary": "फाइबर, साबुत अनाज, प्रोटीन, स्वस्थ वसा और नमक नियंत्रण पर वैज्ञानिक आहार मार्गदर्शन।",
                "content": (
                    "संतुलित आहार में सब्जियाँ, फल, साबुत अनाज, दालें, मेवे और लीन प्रोटीन शामिल होते हैं, जबकि अतिरिक्त चीनी, अधिक नमक और ट्रांस फैट कम रखे जाते हैं।\n\n"
                    "फाइबर पाचन को बेहतर बनाता है, ब्लड शुगर को स्थिर रखने में मदद करता है और कोलेस्ट्रॉल को नियंत्रित रखता है।"
                ),
                "key_takeaways": [
                    "अपनी थाली का आधा हिस्सा रंग-बिरंगी सब्जियों और फलों से भरें।",
                    "सैचुरेटेड फैट के बजाय मेवे, जैतून का तेल या स्वस्थ वसा चुनें।",
                    "ब्लड प्रेशर के लिए नमक और प्रोसेस्ड फूड कम खाएँ।",
                ],
                "when_to_see_doctor": "यदि आपको किडनी रोग, डायबिटीज या फूड एलर्जी है, तो आहार में बड़े बदलाव से पहले डॉक्टर या डाइटीशियन से पूछें।",
            },
        },
    },
    {
        "id": "nut-hydration-electrolytes",
        "category": "Nutrition",
        "read_minutes": 4,
        "source_name": "MedlinePlus Fluid & Electrolyte Balance",
        "source_url": "https://medlineplus.gov/fluidandelectrolytebalance.html",
        "translations": {
            "en": {
                "title": "Hydration Basics and Recognizing Mild Dehydration",
                "summary": "How fluid needs change with heat, exercise, and illness, and when oral rehydration matters.",
                "content": (
                    "Water makes up more than half of the human body and is essential for temperature regulation, joint lubrication, and nutrient transport. "
                    "Thirst and pale-yellow urine are practical everyday hydration indicators for most healthy adults.\n\n"
                    "During fever, vomiting, diarrhea, or heavy sweating, replacing both fluids and electrolytes is important."
                ),
                "key_takeaways": [
                    "Sip water consistently throughout the day rather than all at once.",
                    "Increase fluid intake during hot weather, exercise, or fever.",
                    "Seek care if unable to keep fluids down for more than 24 hours.",
                ],
                "when_to_see_doctor": "Seek urgent care for dizziness on standing, confusion, very dark or absent urination, or persistent vomiting.",
            },
            "te": {
                "title": "శరీరంలో నీటి సమతుల్యత మరియు డీహైడ్రేషన్ గుర్తింపు",
                "summary": "ఎండలు, వ్యాయామం మరియు జ్వరం సమయంలో నీరు మరియు ఎలక్ట్రోలైట్ల అవసరం ఎలా మారుతుందో తెలుసుకోండి.",
                "content": (
                    "మన శరీరంలో సగానికి పైగా నీరు ఉంటుంది. శరీర ఉష్ణోగ్రత నియంత్రణకు మరియు పోషకాల రవాణాకు నీరు చాలా అవసరం. లేత పసుపు రంగు మూత్రం సాధారణ హైడ్రేషన్‌కు సూచన.\n\n"
                    "జ్వరం, వాంతులు, విరేచనాలు లేదా ఎక్కువ చెమట వచ్చినప్పుడు నీటితో పాటు ORS వంటి ఎలక్ట్రోలైట్లు తీసుకోవడం ముఖ్యం."
                ),
                "key_takeaways": [
                    "రోజంతా కొద్దికొద్దిగా నిరంతరం నీరు త్రాగండి.",
                    "ఎండలో, వ్యాయామంలో లేదా జ్వరంలో ద్రవాలు ఎక్కువగా తీసుకోండి.",
                    "24 గంటలకు మించి నీరు నిలబడకపోతే వైద్య సహాయం తీసుకోండి.",
                ],
                "when_to_see_doctor": "నిలబడినప్పుడు కళ్లు తిరగడం, గందరగోళం, మూత్రం చాలా తగ్గడం లేదా ఆగని వాంతులు ఉంటే వెంటనే డాక్టర్‌ను సంప్రదించండి.",
            },
            "hi": {
                "title": "हाइड्रेशन के नियम और पानी की कमी (डीहाइड्रेशन) की पहचान",
                "summary": "गर्मी, व्यायाम और बीमारी में तरल पदार्थ व इलेक्ट्रोलाइट्स की जरूरत कैसे बदलती है।",
                "content": (
                    "मानव शरीर का आधे से अधिक हिस्सा पानी से बना है, जो शरीर का तापमान नियंत्रित रखने और पोषक तत्व पहुंचाने के लिए आवश्यक है। हल्का पीला मूत्र सामान्य हाइड्रेशन का संकेत है।\n\n"
                    "बुखार, उल्टी, दस्त या अत्यधिक पसीने के दौरान पानी के साथ इलेक्ट्रोलाइट्स (जैसे ORS) लेना ज़रूरी होता है।"
                ),
                "key_takeaways": [
                    "दिन भर में थोड़ा-थोड़ा पानी लगातार पिएँ।",
                    "गर्मी, कसरत या बुखार के समय तरल पदार्थ बढ़ाएँ।",
                    "यदि 24 घंटे से अधिक तरल पदार्थ पेट में न टिकें तो डॉक्टर से मिलें।",
                ],
                "when_to_see_doctor": "खड़े होने पर चक्कर आना, भ्रम, बहुत कम या गहरे रंग का पेशाब या लगातार उल्टी होने पर तुरंत चिकित्सा सहायता लें।",
            },
        },
    },
    {
        "id": "fit-physical-activity-guidelines",
        "category": "Fitness and Exercise",
        "read_minutes": 5,
        "source_name": "WHO Physical Activity",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/physical-activity",
        "translations": {
            "en": {
                "title": "Weekly Physical Activity Guidelines for Adults",
                "summary": "How moderate aerobic movement and muscle-strengthening activities reduce chronic disease risk.",
                "content": (
                    "WHO and CDC guidelines recommend at least 150 minutes of moderate-intensity aerobic activity (such as brisk walking or cycling) "
                    "per week, combined with muscle-strengthening activities on 2 or more days.\n\n"
                    "Even short 10-minute movement breaks improve insulin sensitivity, mood, and joint mobility."
                ),
                "key_takeaways": [
                    "Target 150 minutes/week of moderate aerobic exercise or 75 minutes vigorous.",
                    "Include strength training for major muscle groups twice weekly.",
                    "Reduce prolonged sitting with short walking or stretching breaks.",
                ],
                "when_to_see_doctor": "Check with a clinician before starting vigorous exercise if you have chest discomfort, dizziness, or chronic heart/lung conditions.",
            },
            "te": {
                "title": "పెద్దల కోసం వారాంతపు శారీరక వ్యాయామ మార్గదర్శకాలు",
                "summary": "నడక మరియు కండరాలను బలపరిచే వ్యాయామాలు దీర్ఘకాలిక వ్యాధుల ప్రమాదాన్ని ఎలా తగ్గిస్తాయి.",
                "content": (
                    "WHO మరియు CDC మార్గదర్శకాల ప్రకారం వారానికి కనీసం 150 నిమిషాలు మధ్యస్థ స్థాయి వ్యాయామం (వేగవంతమైన నడక, సైక్లింగ్) మరియు వారానికి 2 రోజులు కండరాల బలం పెంచే వ్యాయామాలు చేయాలి.\n\n"
                    "రోజులో 10 నిమిషాల చిన్న నడక విరామాలు కూడా రక్తంలో చక్కెర నియంత్రణకు మరియు మానసిక ఉత్సాహానికి మేలు చేస్తాయి."
                ),
                "key_takeaways": [
                    "వారానికి 150 నిమిషాల మధ్యస్థ వ్యాయామం లక్ష్యంగా పెట్టుకోండి.",
                    "వారంలో కనీసం రెండుసార్లు స్ట్రెంగ్త్ ట్రైనింగ్ చేయండి.",
                    "ఎక్కువ సేపు కూర్చోకుండా మధ్యలో లేచి నడవండి.",
                ],
                "when_to_see_doctor": "వ్యాయామంలో ఛాతీ అసౌకర్యం, తలతిరగడం లేదా గుండె/ఊపిరితిత్తుల సమస్యలు ఉంటే ముందుగా డాక్టర్ సలహా తీసుకోండి.",
            },
            "hi": {
                "title": "वयस्कों के लिए साप्ताहिक शारीरिक गतिविधि दिशानिर्देश",
                "summary": "नियमित एरोबिक व्यायाम और स्ट्रेंथ ट्रेनिंग से पुरानी बीमारियों का जोखिम कैसे कम होता है।",
                "content": (
                    "WHO और CDC के अनुसार हर सप्ताह कम से कम 150 मिनट की मध्यम एरोबिक गतिविधि (जैसे तेज चलना या साइकिल चलाना) और सप्ताह में 2 दिन मांसपेशियों को मजबूत करने वाले व्यायाम करने चाहिए।\n\n"
                    "10-10 मिनट की छोटी चहलकदमी भी इंसुलिन संवेदनशीलता, मूड और जोड़ों की लचीलापन में सुधार करती है।"
                ),
                "key_takeaways": [
                    "सप्ताह में 150 मिनट मध्यम व्यायाम का लक्ष्य रखें।",
                    "सप्ताह में दो बार प्रमुख मांसपेशियों के लिए स्ट्रेंथ व्यायाम करें।",
                    "लगातार बैठने से बचें और बीच-बीच में टहलें।",
                ],
                "when_to_see_doctor": "यदि आपको सीने में असुविधा, चक्कर आना या हृदय/फेफड़ों की समस्या है तो कठिन व्यायाम से पहले डॉक्टर से सलाह लें।",
            },
        },
    },
    {
        "id": "fit-safe-injury-prevention",
        "category": "Fitness and Exercise",
        "read_minutes": 4,
        "source_name": "MedlinePlus Exercise & Physical Fitness",
        "source_url": "https://medlineplus.gov/exerciseandphysicalfitness.html",
        "translations": {
            "en": {
                "title": "Preventing Exercise Strain and Joint Overuse Injuries",
                "summary": "Warm-ups, progressive overload, proper footwear, and knowing normal soreness versus warning pain.",
                "content": (
                    "Gradual progression—increasing workout duration or intensity by small increments—helps tendons, ligaments, and muscles adapt safely. "
                    "A 5–10 minute dynamic warm-up prepares joints and circulation before heavier exertion.\n\n"
                    "Mild muscle soreness 24–48 hours after new exercise is normal, whereas sharp joint pain, swelling, or instability signals a need to rest and evaluate."
                ),
                "key_takeaways": [
                    "Warm up before workouts and prioritize proper form over heavy load.",
                    "Schedule rest days for muscle recovery.",
                    "Stop exercising immediately if you feel sharp pain, dizziness, or chest tightness.",
                ],
                "when_to_see_doctor": "Seek medical evaluation for joint swelling, inability to bear weight, or pain that worsens over several days.",
            },
            "te": {
                "title": "వ్యాయామ గాయాలు మరియు కీళ్ల నొప్పుల నివారణ",
                "summary": "వార్మ్-అప్, విశ్రాంతి రోజులు మరియు సాధారణ కండరాల నొప్పి vs ప్రమాద నొప్పిని గుర్తించడం.",
                "content": (
                    "వ్యాయామ సమయాన్ని లేదా తీవ్రతను నెమ్మదిగా పెంచడం వల్ల కండరాలు మరియు కీళ్లు సురక్షితంగా అలవాటు పడతాయి. వ్యాయామానికి ముందు 5–10 నిమిషాల వార్మ్-అప్ చాలా ముఖ్యం.\n\n"
                    "కొత్త వ్యాయామం తర్వాత 1–2 రోజులు తేలికపాటి కండరాల నొప్పి సహజమే; కానీ కీళ్లలో వాపు, తీవ్రమైన నొప్పి ఉంటే వెంటనే ఆపి విశ్రాంతి తీసుకోవాలి."
                ),
                "key_takeaways": [
                    "వ్యాయామం ముందు వార్మ్-అప్ మరియు సరైన భంగిమను పాటించండి.",
                    "కండరాలు కోలుకోవడానికి విశ్రాంతి రోజులు కేటాయించండి.",
                    "తీవ్రమైన నొప్పి, తలతిరగడం లేదా ఛాతీ బిగుతు వస్తే వెంటనే ఆపండి.",
                ],
                "when_to_see_doctor": "కీళ్ల వాపు, కాలు మోపలేకపోవడం లేదా కొన్ని రోజులుగా నొప్పి పెరుగుతుంటే డాక్టర్‌ను కలవండి.",
            },
            "hi": {
                "title": "व्यायाम के दौरान चोट और जोड़ों के खिंचाव से बचाव",
                "summary": "वार्म-अप, सही तकनीक और सामान्य मांसपेशी दर्द बनाम चेतावनी वाले दर्द की पहचान।",
                "content": (
                    "व्यायाम की अवधि या तीव्रता धीरे-धीरे बढ़ाने से मांसपेशियाँ और जोड़ सुरक्षित रहते हैं। कसरत से पहले 5–10 मिनट का वार्म-अप बहुत उपयोगी है।\n\n"
                    "नए व्यायाम के 24–48 घंटे बाद हल्का दर्द सामान्य है, लेकिन जोड़ों में सूजन या तेज दर्द होने पर तुरंत रुकें।"
                ),
                "key_takeaways": [
                    "कसरत से पहले वार्म-अप करें और सही मुद्रा बनाए रखें।",
                    "मांसपेशियों की रिकवरी के लिए विश्राम के दिन रखें।",
                    "तेज दर्द, चक्कर या सीने में जकड़न महसूस होने पर तुरंत रुक जाएँ।",
                ],
                "when_to_see_doctor": "जोड़ों में सूजन, वजन न संभाल पाना या कई दिनों तक दर्द बढ़ने पर डॉक्टर को दिखाएँ।",
            },
        },
    },
    {
        "id": "prev-screenings-immunizations",
        "category": "Preventive Healthcare",
        "read_minutes": 6,
        "source_name": "CDC Preventive Care",
        "source_url": "https://www.cdc.gov/chronic-disease/prevention/index.html",
        "translations": {
            "en": {
                "title": "Preventive Health Screenings and Routine Checkups",
                "summary": "Why blood pressure checks, lipid panels, cancer screenings, and recommended vaccines protect long-term health.",
                "content": (
                    "Preventive care focuses on detecting silent risk factors early—such as elevated blood pressure, high cholesterol, or prediabetes—before "
                    "complications develop. Recommended screenings depend on age, sex, family history, and personal risk factors.\n\n"
                    "Keeping vaccinations current also reduces the severity of preventable respiratory and viral illnesses."
                ),
                "key_takeaways": [
                    "Schedule annual or clinician-recommended preventive wellness visits.",
                    "Track blood pressure, blood sugar, and cholesterol trends over time.",
                    "Discuss age-appropriate cancer screenings and immunizations with your doctor.",
                ],
                "when_to_see_doctor": "Ask your primary care clinician for a personalized screening schedule based on your age and family history.",
            },
            "te": {
                "title": "నివారణ ఆరోగ్య పరీక్షలు మరియు సాధారణ చెకప్‌లు",
                "summary": "రక్తపోటు, కొలెస్ట్రాల్, షుగర్ పరీక్షలు మరియు టీకాలు దీర్ఘకాలిక ఆరోగ్యాన్ని ఎలా కాపాడతాయి.",
                "content": (
                    "ప్రివెంటివ్ కేర్ లక్ష్యం అధిక రక్తపోటు, అధిక కొలెస్ట్రాల్ లేదా ప్రీ-డయాబెటిస్ వంటి లక్షణాలు కనిపించని ప్రమాదాలను ముందుగానే గుర్తించడం.\n\n"
                    "వయస్సు, కుటుంబ ఆరోగ్య చరిత్ర ఆధారంగా క్రమమైన పరీక్షలు మరియు సూచించిన టీకాలు తీసుకోవడం తీవ్రమైన వ్యాధుల నుండి రక్షిస్తుంది."
                ),
                "key_takeaways": [
                    "సంవత్సరానికి ఒకసారి లేదా డాక్టర్ సూచన మేరకు సాధారణ ఆరోగ్య పరీక్షలు చేయించుకోండి.",
                    "బీపీ, షుగర్, కొలెస్ట్రాల్ విలువలను నమోదు చేసి ట్రాక్ చేయండి.",
                    "మీ వయస్సుకు తగిన స్క్రీనింగ్‌లు మరియు వ్యాక్సిన్ల గురించి డాక్టర్‌ను అడగండి.",
                ],
                "when_to_see_doctor": "మీ వయస్సు మరియు కుటుంబ చరిత్ర ఆధారంగా సరైన పరీక్షల షెడ్యూల్ కోసం మీ ఫ్యామిలీ డాక్టర్‌ను సంప్రదించండి.",
            },
            "hi": {
                "title": "निवारक स्वास्थ्य जांच और नियमित चेकअप",
                "summary": "ब्लड प्रेशर, कोलेस्ट्रॉल, शुगर जांच और टीकाकरण दीर्घकालिक स्वास्थ्य की रक्षा कैसे करते हैं।",
                "content": (
                    "निवारक देखभाल का उद्देश्य बिना लक्षण वाले जोखिमों—जैसे उच्च रक्तचाप, बढ़ा कोलेस्ट्रॉल या प्रीडायबिटीज—को जटिलताओं से पहले पहचानना है।\n\n"
                    "उम्र और पारिवारिक इतिहास के अनुसार नियमित जांच और समय पर टीकाकरण गंभीर बीमारियों से बचाते हैं।"
                ),
                "key_takeaways": [
                    "सालाना या डॉक्टर की सलाह के अनुसार स्वास्थ्य जांच कराएँ।",
                    "बीपी, ब्लड शुगर और कोलेस्ट्रॉल के रिकॉर्ड सहेज कर रखें।",
                    "अपनी उम्र के अनुसार स्क्रीनिंग और टीकों के बारे में डॉक्टर से पूछें।",
                ],
                "when_to_see_doctor": "अपनी उम्र और पारिवारिक इतिहास के अनुसार जांच की सूची के लिए अपने डॉक्टर से मिलें।",
            },
        },
    },
    {
        "id": "prev-hand-respiratory-hygiene",
        "category": "Preventive Healthcare",
        "read_minutes": 4,
        "source_name": "CDC Hygiene & Prevention",
        "source_url": "https://www.cdc.gov/hygiene/about/index.html",
        "translations": {
            "en": {
                "title": "Everyday Infection Prevention and Respiratory Hygiene",
                "summary": "Evidence-based habits that lower the spread of seasonal respiratory and gastrointestinal infections.",
                "content": (
                    "Washing hands with soap and water for at least 20 seconds, covering coughs and sneezes, improving indoor ventilation, and staying home when "
                    "febrile significantly reduce infection transmission.\n\n"
                    "Proper food handling—separating raw meats, washing produce, and refrigerating leftovers promptly—also prevents common foodborne illnesses."
                ),
                "key_takeaways": [
                    "Wash hands thoroughly before eating and after coughing or using public spaces.",
                    "Ventilate shared indoor rooms when respiratory viruses are circulating.",
                    "Never take leftover antibiotics without a clinician's evaluation.",
                ],
                "when_to_see_doctor": "Seek care for persistent high fever, shortness of breath, dehydration, or symptoms that worsen after initial improvement.",
            },
            "te": {
                "title": "రోజువారీ ఇన్ఫెక్షన్ నివారణ మరియు శ్వాసకోశ పరిశుభ్రత",
                "summary": "జలుబు, ఫ్లూ మరియు కడుపు ఇన్ఫెక్షన్ల వ్యాప్తిని తగ్గించే సులభమైన పరిశుభ్రత అలవాట్లు.",
                "content": (
                    "తినే ముందు మరియు బయట నుండి వచ్చిన తర్వాత కనీసం 20 సెకన్లు సబ్బుతో చేతులు కడుక్కోవడం, దగ్గినప్పుడు/తుమ్మినప్పుడు నోరు కప్పుకోవడం, గదులలో గాలి ప్రసరణ ఉండేలా చూడటం ఇన్ఫెక్షన్లను తగ్గిస్తాయి.\n\n"
                    "డాక్టర్ సలహా లేకుండా పాత యాంటీబయాటిక్స్ ఎప్పుడూ వాడకూడదు."
                ),
                "key_takeaways": [
                    "భోజనానికి ముందు, బాత్రూమ్ తర్వాత చేతులు శుభ్రంగా కడుక్కోండి.",
                    "ఇంట్లో మరియు గదులలో స్వచ్ఛమైన గాలి వచ్చేలా చూడండి.",
                    "డాక్టర్ సూచన లేకుండా యాంటీబయాటిక్స్ వాడకండి.",
                ],
                "when_to_see_doctor": "తగ్గని అధిక జ్వరం, శ్వాస ఇబ్బంది, లేదా లక్షణాలు మళ్లీ పెరిగితే డాక్టర్‌ను కలవండి.",
            },
            "hi": {
                "title": "दैनिक संक्रमण रोकथाम और श्वसन स्वच्छता",
                "summary": "मौसमी वायरल, फ्लू और पेट के संक्रमण को कम करने वाली आसान स्वच्छता आदतें।",
                "content": (
                    "खाने से पहले और बाहर से आने पर कम से कम 20 सेकंड तक साबुन से हाथ धोना, खांसते या छींकते समय मुंह ढकना और कमरों में हवादार माहौल रखना संक्रमण को काफी कम करता है।\n\n"
                    "बिना डॉक्टर की जांच के कभी भी बची हुई एंटीबायोटिक्स न लें।"
                ),
                "key_takeaways": [
                    "खाने से पहले और सार्वजनिक स्थानों से आने पर अच्छी तरह हाथ धोएँ।",
                    "बंद कमरों में वेंटिलेशन बनाए रखें।",
                    "डॉक्टर की सलाह के बिना एंटीबायोटिक्स का उपयोग न करें।",
                ],
                "when_to_see_doctor": "लगातार तेज बुखार, सांस लेने में तकलीफ या पानी की कमी होने पर डॉक्टर से संपर्क करें।",
            },
        },
    },
    {
        "id": "cond-hypertension-basics",
        "category": "Common Health Conditions",
        "read_minutes": 5,
        "source_name": "MedlinePlus High Blood Pressure",
        "source_url": "https://medlineplus.gov/highbloodpressure.html",
        "translations": {
            "en": {
                "title": "Understanding High Blood Pressure (Hypertension)",
                "summary": "What systolic and diastolic numbers mean, why hypertension often has no symptoms, and lifestyle management.",
                "content": (
                    "Blood pressure measures the force of blood pushing against artery walls. The top number (systolic) reflects pressure during heartbeats, "
                    "and the bottom number (diastolic) reflects pressure between beats.\n\n"
                    "Because hypertension rarely causes noticeable symptoms on its own, regular monitoring is key."
                ),
                "key_takeaways": [
                    "Rest quietly for 5 minutes before taking a home blood pressure reading.",
                    "Keep a log of home readings to share at medical appointments.",
                    "Never stop prescribed blood pressure medication abruptly without consulting your doctor.",
                ],
                "when_to_see_doctor": "Seek emergency care if extremely high readings occur alongside chest pain, severe headache, vision changes, or shortness of breath.",
            },
            "te": {
                "title": "అధిక రక్తపోటు (హై బీపీ) గురించి అవగాహన",
                "summary": "సిస్టోలిక్ మరియు డయాస్టోలిక్ సంఖ్యల అర్థం, బీపీ ఎందుకు నిశ్శబ్దంగా ఉంటుందో మరియు జీవనశైలి జాగ్రత్తలు.",
                "content": (
                    "రక్తపోటు (BP) రక్తనాళాల గోడలపై రక్తం కలిగించే ఒత్తిడిని కొలుస్తుంది. పై సంఖ్య (సిస్టోలిక్) గుండె కొట్టుకున్నప్పటి ఒత్తిడిని, కింది సంఖ్య (డయాస్టోలిక్) విశ్రాంతి మధ్య ఒత్తిడిని చూపుతుంది.\n\n"
                    "హై బీపీకి చాలాసార్లు బయటకు లక్షణాలు కనిపించవు కాబట్టి క్రమం తప్పకుండా పరీక్షించుకోవడం అవసరం."
                ),
                "key_takeaways": [
                    "ఇంట్లో బీపీ చూసుకునే ముందు 5 నిమిషాలు ప్రశాంతంగా విశ్రాంతి తీసుకోండి.",
                    "మీ రీడింగ్లను ఒక డైరీలో రాసి డాక్టర్‌కు చూపించండి.",
                    "డాక్టర్ సలహా లేకుండా బీపీ మందులు ఆకస్మికంగా ఆపకండి.",
                ],
                "when_to_see_doctor": "చాలా ఎక్కువ బీపీతో పాటు ఛాతీ నొప్పి, తీవ్రమైన తలనొప్పి, చూపు మసకబారడం లేదా శ్వాస ఇబ్బంది ఉంటే వెంటనే అత్యవసర చికిత్స పొందండి.",
            },
            "hi": {
                "title": "उच्च रक्तचाप (हाई ब्लड प्रेशर) को समझना",
                "summary": "सिस्टोलिक और डायस्टोलिक संख्याओं का अर्थ, इसके छिपे हुए जोखिम और जीवनशैली प्रबंधन।",
                "content": (
                    "ब्लड प्रेशर धमनियों की दीवारों पर रक्त के दबाव को मापता है। ऊपर की संख्या (सिस्टोलिक) धड़कन के समय का दबाव और नीचे की संख्या (डायस्टोलिक) धड़कनों के बीच का दबाव दर्शाती है।\n\n"
                    "हाई बीपी में अक्सर स्पष्ट लक्षण नहीं दिखते, इसलिए नियमित जांच सबसे सुरक्षित उपाय है।"
                ),
                "key_takeaways": [
                    "घर पर बीपी मापने से पहले 5 मिनट शांत बैठें।",
                    "रीडिंग का लॉग बनाएँ और डॉक्टर को दिखाएँ।",
                    "डॉक्टर से पूछे बिना बीपी की दवाइयाँ अचानक बंद न करें।",
                ],
                "when_to_see_doctor": "बहुत अधिक बीपी के साथ सीने में दर्द, तेज सिरदर्द, धुंधला दिखना या सांस फूलने पर तुरंत इमरजेंसी में जाएँ।",
            },
        },
    },
    {
        "id": "cond-type2-diabetes-overview",
        "category": "Common Health Conditions",
        "read_minutes": 6,
        "source_name": "WHO Diabetes Fact Sheet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
        "translations": {
            "en": {
                "title": "Understanding Blood Sugar, HbA1c, and Type 2 Diabetes",
                "summary": "How fasting glucose and HbA1c reflect blood sugar patterns and everyday steps for metabolic wellness.",
                "content": (
                    "Glucose is the body's main energy source, regulated by insulin. While a fasting blood glucose test shows a single moment in time, "
                    "Hemoglobin A1c (HbA1c) estimates average blood sugar levels over roughly the past 2 to 3 months.\n\n"
                    "Balanced carbohydrate portions, fiber, regular movement, and healthy sleep meaningfully support blood sugar control."
                ),
                "key_takeaways": [
                    "HbA1c reflects a 2–3 month average rather than a single meal's impact.",
                    "Pair carbohydrates with fiber, protein, or healthy fats to smooth glucose spikes.",
                    "Regular eye, kidney, and foot checks are important for people living with diabetes.",
                ],
                "when_to_see_doctor": "Consult a doctor for excessive thirst, frequent urination, unexplained weight loss, blurry vision, or slow-healing sores.",
            },
            "te": {
                "title": "రక్తంలో చక్కెర, HbA1c మరియు టైప్ 2 మధుమేహం",
                "summary": "ఫాస్టింగ్ షుగర్ మరియు 3 నెలల సగటు చూపే HbA1c పరీక్షల మధ్య తేడా మరియు ఆరోగ్యకరమైన నియంత్రణ.",
                "content": (
                    "గ్లూకోజ్ శరీరానికి ప్రధాన శక్తి వనరు. ఫాస్టింగ్ బ్లడ్ షుగర్ ఆ సమయానికి మాత్రమే చక్కెర స్థాయిని చూపితే, HbA1c పరీక్ష గత 2 నుండి 3 నెలల సగటు చక్కెర స్థాయిని చూపిస్తుంది.\n\n"
                    "ఫైబర్ అధికంగా ఉండే ఆహారం, సమతుల్య పిండిపదార్థాలు, రోజూ నడక మరియు మంచి నిద్ర షుగర్ నియంత్రణలో సహాయపడతాయి."
                ),
                "key_takeaways": [
                    "HbA1c అనేది గత 2–3 నెలల సగటు చక్కెర స్థాయిని చూపుతుంది.",
                    "అన్నం/కార్బోహైడ్రేట్లతో పాటు కూరగాయలు, పప్పులు (ఫైబర్ & ప్రోటీన్) తీసుకోండి.",
                    "మధుమేహం ఉన్నవారు క్రమంగా కళ్ళు, కిడ్నీ మరియు పాదాల పరీక్షలు చేయించుకోవాలి.",
                ],
                "when_to_see_doctor": "అధిక దాహం, తరచుగా మూత్ర విసర్జన, బరువు తగ్గడం, చూపు మసకబారడం లేదా గాయాలు ఆలస్యంగా మానడం ఉంటే డాక్టర్‌ను కలవండి.",
            },
            "hi": {
                "title": "ब्लड शुगर, HbA1c और टाइप 2 डायबिटीज को समझना",
                "summary": "फास्टिंग शुगर और 3 महीने का औसत दिखाने वाले HbA1c टेस्ट में अंतर और शुगर नियंत्रण के उपाय।",
                "content": (
                    "ग्लूकोज शरीर की मुख्य ऊर्जा है। जहाँ फास्टिंग ब्लड शुगर किसी एक समय का स्तर दिखाता है, वहीं HbA1c पिछले लगभग 2 से 3 महीनों के औसत ब्लड शुगर स्तर को दर्शाता है।\n\n"
                    "फाइबर युक्त भोजन, संतुलित कार्बोहाइड्रेट, नियमित टहलना और अच्छी नींद इंसुलिन संवेदनशीलता बेहतर करते हैं।"
                ),
                "key_takeaways": [
                    "HbA1c पिछले 2–3 महीनों का औसत शुगर स्तर बताता है।",
                    "कार्बोहाइड्रेट के साथ फाइबर और प्रोटीन शामिल करें।",
                    "डायबिटीज में आँख, किडनी और पैरों की नियमित जांच कराते रहें।",
                ],
                "when_to_see_doctor": "अत्यधिक प्यास, बार-बार पेशाब, बिना कारण वजन घटना, धुंधला दिखना या घाव देर से भरने पर डॉक्टर को दिखाएँ।",
            },
        },
    },
    {
        "id": "ment-stress-and-anxiety",
        "category": "Mental Wellness",
        "read_minutes": 5,
        "source_name": "WHO Mental Health",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response",
        "translations": {
            "en": {
                "title": "Managing Everyday Stress and Recognizing Anxiety",
                "summary": "How chronic stress affects sleep, digestion, and heart rate, plus evidence-based coping strategies.",
                "content": (
                    "Short-term stress is a natural response to demands, but prolonged stress can contribute to muscle tension, poor sleep, headaches, "
                    "digestive upset, and emotional exhaustion.\n\n"
                    "Structured breathing exercises, regular physical movement, social connection, mindfulness, and counseling help restore balance."
                ),
                "key_takeaways": [
                    "Slow paced breathing (e.g., 4-second inhale, 6-second exhale) helps reduce acute tension.",
                    "Physical exercise and consistent sleep strongly support emotional resilience.",
                    "Reaching out to a mental health professional is a proactive step for health.",
                ],
                "when_to_see_doctor": "Seek professional support if anxiety or worry persists for weeks or disrupts daily life. In crisis, contact emergency services immediately.",
            },
            "te": {
                "title": "రోజువారీ ఒత్తిడిని తగ్గించుకోవడం మరియు ఆందోళనను గుర్తించడం",
                "summary": "దీర్ఘకాలిక ఒత్తిడి నిద్ర మరియు శరీరంపై ఎలా ప్రభావం చూపుతుంది మరియు మనసును ప్రశాంతపరిచే మార్గాలు.",
                "content": (
                    "తాత్కాలిక ఒత్తిడి సహజమే అయినా, దీర్ఘకాలిక ఒత్తిడి నిద్రలేమి, తలనొప్పి, కండరాల బిగుతు మరియు జీర్ణ సమస్యలకు దారితీయవచ్చు.\n\n"
                    "నెమ్మదైన శ్వాస వ్యాయామాలు, వ్యాయామం, కుటుంబ సభ్యులు/స్నేహితులతో మాట్లాడటం మరియు కౌన్సెలింగ్ మానసిక ప్రశాంతతను పెంచుతాయి."
                ),
                "key_takeaways": [
                    "నెమ్మదిగా గాలి పీల్చి వదలడం (4 సెకన్లు లోపలికి, 6 సెకన్లు బయటకు) ఒత్తిడిని తగ్గిస్తుంది.",
                    "క్రమమైన వ్యాయామం మరియు నిద్ర మానసిక ఆరోగ్యాన్ని బలపరుస్తాయి.",
                    "మానసిక ఆరోగ్య నిపుణుల సహాయం తీసుకోవడం మంచి నిర్ణయం.",
                ],
                "when_to_see_doctor": "ఆందోళన వారాల తరబడి ఉండి రోజువారీ పనులకు ఆటంకం కలిగిస్తే డాక్టర్ లేదా కౌన్సెలర్‌ను సంప్రదించండి.",
            },
            "hi": {
                "title": "दैनिक तनाव का प्रबंधन और चिंता (Anxiety) की पहचान",
                "summary": "लगातार तनाव नींद व शरीर पर कैसे असर डालता है और मन को शांत रखने के वैज्ञानिक तरीके।",
                "content": (
                    "अल्पकालिक तनाव सामान्य है, लेकिन लंबे समय तक तनाव रहने से नींद की कमी, सिरदर्द, मांसपेशियों में जकड़न और पाचन समस्याएँ हो सकती हैं।\n\n"
                    "गहरी और धीमी सांस के अभ्यास, नियमित व्यायाम, अपनों से बातचीत और काउंसलिंग मानसिक संतुलन बनाए रखने में मदद करते हैं।"
                ),
                "key_takeaways": [
                    "धीमी सांस (4 सेकंड अंदर, 6 सेकंड बाहर) तनाव को तुरंत कम करती है।",
                    "व्यायाम और नियमित नींद मानसिक मजबूती बढ़ाते हैं।",
                    "मानसिक स्वास्थ्य विशेषज्ञ से बात करना एक सकारात्मक कदम है।",
                ],
                "when_to_see_doctor": "यदि चिंता कई हफ्तों तक बनी रहे और दैनिक जीवन को प्रभावित करे तो डॉक्टर या काउंसलर से सलाह लें।",
            },
        },
    },
    {
        "id": "ment-burnout-and-mood",
        "category": "Mental Wellness",
        "read_minutes": 5,
        "source_name": "MedlinePlus Mental Health",
        "source_url": "https://medlineplus.gov/mentalhealth.html",
        "translations": {
            "en": {
                "title": "Recognizing Depression, Burnout, and When to Seek Support",
                "summary": "Understanding common signs of persistent low mood and practical pathways to compassionate clinical care.",
                "content": (
                    "Persistent sadness, loss of interest in enjoyable activities, changes in appetite or sleep, fatigue, and difficulty concentrating "
                    "can be signs of depression or significant burnout—not personal weakness.\n\n"
                    "Primary care doctors, psychologists, and counselors can screen for medical contributors and offer effective support."
                ),
                "key_takeaways": [
                    "Track mood, sleep, and energy patterns over 2 weeks to share with a clinician.",
                    "Stay connected with trusted friends, family, or support networks.",
                    "Immediate help is available 24/7 through local crisis hotlines and emergency services.",
                ],
                "when_to_see_doctor": "If you ever have thoughts of self-harm or suicide, contact emergency services or a crisis line immediately.",
            },
            "te": {
                "title": "డిప్రెషన్, బర్నౌట్ గుర్తింపు మరియు సహాయం ఎప్పుడు తీసుకోవాలి",
                "summary": "దీర్ఘకాలిక నిరాశ లక్షణాలను అర్థం చేసుకోవడం మరియు సరైన వైద్య సహాయం పొందడం.",
                "content": (
                    "రెండు వారాలకు పైగా నిరంతర విచారం, ఇష్టమైన పనులపై ఆసక్తి తగ్గడం, నిద్ర లేదా ఆకలిలో మార్పులు, తీవ్రమైన అలసట బర్నౌట్ లేదా డిప్రెషన్ సంకేతాలు కావచ్చు—ఇది బలహీనత కాదు.\n\n"
                    "డాక్టర్లు మరియు మానసిక నిపుణులు శారీరక కారణాలను (థైరాయిడ్, విటమిన్ లోపాలు వంటివి) పరీక్షించి సరైన మార్గదర్శకత్వం అందిస్తారు."
                ),
                "key_takeaways": [
                    "2 వారాల పాటు మీ నిద్ర, మూడ్ మరియు శక్తి స్థాయిలను గమనించండి.",
                    "నమ్మకమైన కుటుంబ సభ్యులు లేదా స్నేహితులతో మాట్లాడండి.",
                    "అత్యవసర మానసిక సంక్షోభంలో హెల్ప్‌లైన్ లేదా 112 ను వెంటనే సంప్రదించండి.",
                ],
                "when_to_see_doctor": "స్వీయ-హాని ఆలోచనలు వస్తే వెంటనే అత్యవసర సేవలు లేదా మానసిక ఆరోగ్య హెల్ప్‌లైన్‌కు కాల్ చేయండి.",
            },
            "hi": {
                "title": "अवसाद (Depression) और बर्नआउट की पहचान व सहायता",
                "summary": "लगातार उदासी के सामान्य लक्षण और संवेदनशील चिकित्सीय सहायता लेने के तरीके।",
                "content": (
                    "लगातार उदासी, पसंदीदा कामों में रुचि कम होना, नींद या भूख में बदलाव, थकान और एकाग्रता की कमी डिप्रेशन या बर्नआउट के संकेत हो सकते हैं—यह कमजोरी नहीं है।\n\n"
                    "डॉक्टर और मनोवैज्ञानिक शारीरिक कारणों (जैसे थायरॉइड या विटामिन की कमी) की जांच कर प्रभावी मदद दे सकते हैं।"
                ),
                "key_takeaways": [
                    "2 सप्ताह तक अपने मूड, नींद और ऊर्जा के पैटर्न पर ध्यान दें।",
                    "विश्वसनीय मित्रों और परिवार से जुड़े रहें।",
                    "संकट के समय 24/7 हेल्पलाइन या आपातकालीन सेवा 112 पर संपर्क करें।",
                ],
                "when_to_see_doctor": "यदि कभी भी आत्म-नुकसान के विचार आएँ तो तुरंत आपातकालीन सेवाओं या हेल्पलाइन पर कॉल करें।",
            },
        },
    },
]


def localize_article(article: Dict[str, Any], lang: str) -> Dict[str, Any]:
    tr = article["translations"].get(lang) or article["translations"]["en"]
    minutes = article["read_minutes"]
    read_unit = READ_TIME_LABEL.get(lang, READ_TIME_LABEL["en"])
    cat = article["category"]
    return {
        "id": article["id"],
        "category": cat,
        "category_label": CATEGORY_LABELS.get(cat, {}).get(lang, cat),
        "read_time": f"{minutes} {read_unit}",
        "title": tr["title"],
        "summary": tr["summary"],
        "content": tr["content"],
        "key_takeaways": tr["key_takeaways"],
        "when_to_see_doctor": tr["when_to_see_doctor"],
        "source_name": article["source_name"],
        "source_url": article["source_url"],
    }
