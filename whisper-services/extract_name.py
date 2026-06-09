import re
from transformers import pipeline

ner = pipeline(
    "ner",
    model="Davlan/xlm-roberta-base-ner-hrl",
    grouped_entities=True
)

def extract_name_rules(text):
    patterns = [

        # -----------------
        # ENGLISH
        # -----------------
        r"my name is ([A-Za-z ]+)",
        r"i am ([A-Za-z ]+)",
        r"this is ([A-Za-z ]+)",
        r"it's ([A-Za-z ]+)",

        # -----------------
        # HINDI
        # -----------------
        r"मेरा नाम ([\w ]+) है",
        r"मैं ([\w ]+) हूँ",
        r"ये ([\w ]+) है",

        # -----------------
        # HINGLISH
        # -----------------
        r"mera naam ([A-Za-z ]+)",
        r"main ([A-Za-z ]+)",
        r"mai ([A-Za-z ]+)",

        # -----------------
        # MARATHI
        # -----------------
        r"माझं नाव ([\w ]+) आहे",
        r"मी ([\w ]+) आहे",

        # -----------------
        # TAMIL
        # -----------------
        r"என் பெயர் ([\w ]+)",
        r"நான் ([\w ]+)",

        # -----------------
        # TELUGU
        # -----------------
        r"నా పేరు ([\w ]+)",
        r"నేను ([\w ]+)",

        # -----------------
        # MALAYALAM
        # -----------------
        r"എന്റെ പേര് ([\w ]+)",
        r"ഞാൻ ([\w ]+)",

        # -----------------
        # KANNADA
        # -----------------
        r"ನನ್ನ ಹೆಸರು ([\w ]+)",
        r"ನಾನು ([\w ]+)",

        # -----------------
        # URDU
        # -----------------
        r"میرا نام ([\w ]+)",
        r"میں ([\w ]+) ہوں"
    ]

    text = text.strip()

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            
            # Clean unwanted words
            name = re.sub(r"(है|हूँ|hai|hoon)$", "", name).strip()
            return name

    return None

def extract_name_ner(text):
    results = ner(text)
    
    names = []
    for r in results:
        if r["entity_group"] == "PER":
            names.append(r["word"])
    
    return names

def extract_name(text):
    # 1. Rule-based (fast + high precision)
    name = extract_name_rules(text)
    if name:
        return name
    
    # 2. NER fallback (handles complex sentences)
    names = extract_name_ner(text)
    if names:
        return names[0]
    
    return ""