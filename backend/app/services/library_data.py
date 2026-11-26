"""Curated health education articles across 6 categories with MedlinePlus, WHO, and CDC sources."""

from typing import Dict, List

CATEGORIES: List[str] = [
    "General Health",
    "Nutrition",
    "Fitness and Exercise",
    "Preventive Healthcare",
    "Common Health Conditions",
    "Mental Wellness",
]

ARTICLES: List[Dict[str, object]] = [
    {
        "id": "gen-understanding-lab-tests",
        "title": "Understanding Common Blood Tests and Reference Ranges",
        "category": "General Health",
        "read_time": "5 min read",
        "summary": "Learn what a Complete Blood Count (CBC) and Basic Metabolic Panel (BMP) measure and why reference ranges vary by lab.",
        "content": (
            "Routine blood panels help clinicians evaluate organ function, hydration, electrolyte balance, and blood cell counts. "
            "A reference range represents the typical values seen in a healthy population, though individual baselines, age, sex, and "
            "laboratory methods all influence interpretation.\n\n"
            "Slightly out-of-range numbers do not automatically mean illness—hydration, recent meals, exercise, or medications can shift results. "
            "Always review laboratory reports alongside your clinician, who interprets numbers in the context of your symptoms and medical history."
        ),
        "key_takeaways": [
            "Reference ranges differ slightly between laboratories based on testing equipment.",
            "A single borderline result is often interpreted alongside trends over time.",
            "Bring a list of supplements and medications when discussing lab results.",
        ],
        "when_to_see_doctor": "Contact your healthcare provider promptly if a report flags critical values or if you experience new or worsening symptoms.",
        "source_name": "MedlinePlus (NIH)",
        "source_url": "https://medlineplus.gov/lab-tests/",
    },
    {
        "id": "gen-sleep-hygiene",
        "title": "Healthy Sleep Habits for Immune and Cardiovascular Support",
        "category": "General Health",
        "read_time": "4 min read",
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
        "source_name": "CDC Sleep Health",
        "source_url": "https://www.cdc.gov/sleep/about/index.html",
    },
    {
        "id": "nut-balanced-plate",
        "title": "Building a Balanced, Heart-Friendly Daily Diet",
        "category": "Nutrition",
        "read_time": "5 min read",
        "summary": "Practical evidence-based guidance on fiber, whole grains, lean proteins, healthy fats, and sodium awareness.",
        "content": (
            "A balanced eating pattern emphasizes vegetables, fruits, whole grains, legumes, nuts, and lean protein sources while limiting added sugars, "
            "excess sodium, and trans fats.\n\n"
            "Dietary fiber supports digestive regularity, steadier blood glucose responses, and healthy cholesterol levels. Staying well hydrated with water "
            "also supports kidney and metabolic function."
        ),
        "key_takeaways": [
            "Fill half your plate with colorful non-starchy vegetables and fruits.",
            "Choose unsaturated fats (olive oil, nuts, fatty fish) over saturated fats.",
            "Limit sodium intake and ultra-processed foods to support blood pressure.",
        ],
        "when_to_see_doctor": "Consult a doctor or registered dietitian before making major dietary changes if you have kidney disease, diabetes, or food allergies.",
        "source_name": "WHO Healthy Diet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
    },
    {
        "id": "nut-hydration-electrolytes",
        "title": "Hydration Basics and Recognizing Mild Dehydration",
        "category": "Nutrition",
        "read_time": "4 min read",
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
        "source_name": "MedlinePlus Fluid & Electrolyte Balance",
        "source_url": "https://medlineplus.gov/fluidandelectrolytebalance.html",
    },
    {
        "id": "fit-physical-activity-guidelines",
        "title": "Weekly Physical Activity Guidelines for Adults",
        "category": "Fitness and Exercise",
        "read_time": "5 min read",
        "summary": "How moderate aerobic movement and muscle-strengthening activities reduce chronic disease risk.",
        "content": (
            "WHO and CDC guidelines recommend at least 150 minutes of moderate-intensity aerobic activity (such as brisk walking or cycling) "
            "per week, combined with muscle-strengthening activities on 2 or more days.\n\n"
            "Even short 10-minute movement breaks improve insulin sensitivity, mood, and joint mobility. Start gradually if returning after inactivity."
        ),
        "key_takeaways": [
            "Target 150 minutes/week of moderate aerobic exercise or 75 minutes vigorous.",
            "Include strength training for major muscle groups twice weekly.",
            "Reduce prolonged sitting with short walking or stretching breaks.",
        ],
        "when_to_see_doctor": "Check with a clinician before starting vigorous exercise if you have chest discomfort, dizziness, or chronic heart/lung conditions.",
        "source_name": "WHO Physical Activity",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/physical-activity",
    },
    {
        "id": "fit-safe-injury-prevention",
        "title": "Preventing Exercise Strain and Joint Overuse Injuries",
        "category": "Fitness and Exercise",
        "read_time": "4 min read",
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
        "source_name": "MedlinePlus Exercise & Physical Fitness",
        "source_url": "https://medlineplus.gov/exerciseandphysicalfitness.html",
    },
    {
        "id": "prev-screenings-immunizations",
        "title": "Preventive Health Screenings and Routine Checkups",
        "category": "Preventive Healthcare",
        "read_time": "6 min read",
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
        "source_name": "CDC Preventive Care",
        "source_url": "https://www.cdc.gov/chronic-disease/prevention/index.html",
    },
    {
        "id": "prev-hand-respiratory-hygiene",
        "title": "Everyday Infection Prevention and Respiratory Hygiene",
        "category": "Preventive Healthcare",
        "read_time": "4 min read",
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
        "source_name": "CDC Hygiene & Prevention",
        "source_url": "https://www.cdc.gov/hygiene/about/index.html",
    },
    {
        "id": "cond-hypertension-basics",
        "title": "Understanding High Blood Pressure (Hypertension)",
        "category": "Common Health Conditions",
        "read_time": "5 min read",
        "summary": "What systolic and diastolic numbers mean, why hypertension often has no symptoms, and lifestyle management.",
        "content": (
            "Blood pressure measures the force of blood pushing against artery walls. The top number (systolic) reflects pressure during heartbeats, "
            "and the bottom number (diastolic) reflects pressure between beats.\n\n"
            "Because hypertension rarely causes noticeable symptoms on its own, regular monitoring is key. Balanced nutrition, reduced sodium, regular exercise, "
            "stress management, and prescribed medications (when needed) help protect the heart, brain, and kidneys."
        ),
        "key_takeaways": [
            "Rest quietly for 5 minutes before taking a home blood pressure reading.",
            "Keep a log of home readings to share at medical appointments.",
            "Never stop prescribed blood pressure medication abruptly without consulting your doctor.",
        ],
        "when_to_see_doctor": "Seek emergency care if extremely high readings occur alongside chest pain, severe headache, vision changes, or shortness of breath.",
        "source_name": "MedlinePlus High Blood Pressure",
        "source_url": "https://medlineplus.gov/highbloodpressure.html",
    },
    {
        "id": "cond-type2-diabetes-overview",
        "title": "Understanding Blood Sugar, HbA1c, and Type 2 Diabetes",
        "category": "Common Health Conditions",
        "read_time": "6 min read",
        "summary": "How fasting glucose and HbA1c reflect blood sugar patterns and everyday steps for metabolic wellness.",
        "content": (
            "Glucose is the body's main energy source, regulated by insulin. While a fasting blood glucose test shows a single moment in time, "
            "Hemoglobin A1c (HbA1c) estimates average blood sugar levels over roughly the past 2 to 3 months.\n\n"
            "Early lifestyle measures—balanced carbohydrate portions, fiber, regular movement, and healthy sleep—can meaningfully improve insulin sensitivity."
        ),
        "key_takeaways": [
            "HbA1c reflects a 2–3 month average rather than a single meal's impact.",
            "Pair carbohydrates with fiber, protein, or healthy fats to smooth glucose spikes.",
            "Regular eye, kidney, and foot checks are important for people living with diabetes.",
        ],
        "when_to_see_doctor": "Consult a doctor for excessive thirst, frequent urination, unexplained weight loss, blurry vision, or slow-healing sores.",
        "source_name": "WHO Diabetes Fact Sheet",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
    },
    {
        "id": "ment-stress-and-anxiety",
        "title": "Managing Everyday Stress and Recognizing Anxiety",
        "category": "Mental Wellness",
        "read_time": "5 min read",
        "summary": "How chronic stress affects sleep, digestion, and heart rate, plus evidence-based coping strategies.",
        "content": (
            "Short-term stress is a natural response to demands, but prolonged stress can contribute to muscle tension, poor sleep, headaches, "
            "digestive upset, and emotional exhaustion.\n\n"
            "Structured breathing exercises, regular physical movement, social connection, mindfulness, and setting realistic boundaries help calm "
            "the nervous system. Counseling and evidence-based therapies are effective when stress or anxiety interferes with daily life."
        ),
        "key_takeaways": [
            "Slow paced breathing (e.g., 4-second inhale, 6-second exhale) helps reduce acute tension.",
            "Physical exercise and consistent sleep strongly support emotional resilience.",
            "Reaching out to a mental health professional is a proactive step for health.",
        ],
        "when_to_see_doctor": "Seek professional support if anxiety, low mood, or worry persists for weeks or disrupts work, sleep, or relationships. In crisis, contact emergency services or a crisis helpline immediately.",
        "source_name": "WHO Mental Health",
        "source_url": "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response",
    },
    {
        "id": "ment-burnout-and-mood",
        "title": "Recognizing Depression, Burnout, and When to Seek Support",
        "category": "Mental Wellness",
        "read_time": "5 min read",
        "summary": "Understanding common signs of persistent low mood and practical pathways to compassionate clinical care.",
        "content": (
            "Persistent sadness, loss of interest in enjoyable activities, changes in appetite or sleep, fatigue, and difficulty concentrating "
            "can be signs of depression or significant burnout—not personal weakness.\n\n"
            "Primary care doctors, psychologists, and counselors can screen for medical contributors (such as thyroid or vitamin deficiencies) "
            "and offer effective, individualized support."
        ),
        "key_takeaways": [
            "Track mood, sleep, and energy patterns over 2 weeks to share with a clinician.",
            "Stay connected with trusted friends, family, or support networks.",
            "Immediate help is available 24/7 through local crisis hotlines and emergency services.",
        ],
        "when_to_see_doctor": "If you ever have thoughts of self-harm or suicide, contact emergency services or a crisis line immediately.",
        "source_name": "MedlinePlus Mental Health",
        "source_url": "https://medlineplus.gov/mentalhealth.html",
    },
]
