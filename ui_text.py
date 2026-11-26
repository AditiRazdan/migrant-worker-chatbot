"""Fixed screen text in each language.

These lines are shown exactly as written (the AI does not translate them), so the
safety messages can't be mistranslated. The Tamil and Bengali lines are DRAFTS:
have a native speaker check every line before the pilot.
"""

LANGUAGES = {
    "ta": "தமிழ்",
    "bn": "বাংলা",
    "en": "English",
}

TEXT = {
    "en": {
        "emergency": "🚨 Emergency? Call **995** (ambulance / fire) or **999** (police).",
        "human": "Want to talk to a person? MWC helpline **6536 2692** (24 hours, about 10 languages).",
        "welcome": (
            "Hello! Ask me about salary, work rules, safety or healthcare in Singapore. "
            "I answer using official information from MOM and trusted organisations. "
            "I am a student project, not MOM.\n\n"
            "Please do not share your name, company name or FIN."
        ),
        "placeholder": "Type your question…",
        "error": (
            "Sorry, something went wrong. Please try again, or call the MWC helpline "
            "6536 2692 (24 hours)."
        ),
        "limit": (
            "You have reached the message limit for now. For more help, call the MWC helpline "
            "6536 2692 (24 hours)."
        ),
        "change_language": "Change language",
        "thanks": "Thank you!",
    },
    "ta": {
        "emergency": "🚨 அவசரமா? **995** (ஆம்புலன்ஸ் / தீயணைப்பு) அல்லது **999** (காவல்துறை) அழைக்கவும்.",
        "human": "ஒருவரிடம் பேச வேண்டுமா? MWC உதவி எண் **6536 2692** (24 மணி நேரம், சுமார் 10 மொழிகள்).",
        "welcome": (
            "வணக்கம்! சிங்கப்பூரில் சம்பளம், வேலை விதிகள், பாதுகாப்பு அல்லது மருத்துவம் பற்றி என்னிடம் கேளுங்கள். "
            "MOM மற்றும் நம்பகமான அமைப்புகளின் அதிகாரப்பூர்வ தகவல்களைக் கொண்டு நான் பதில் சொல்கிறேன். "
            "நான் ஒரு மாணவர் திட்டம், MOM அல்ல.\n\n"
            "உங்கள் பெயர், நிறுவனத்தின் பெயர் அல்லது FIN எண்ணைப் பகிர வேண்டாம்."
        ),
        "placeholder": "உங்கள் கேள்வியை டைப் செய்யுங்கள்…",
        "error": (
            "மன்னிக்கவும், ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும், அல்லது MWC உதவி எண் "
            "6536 2692 (24 மணி நேரம்) அழைக்கவும்."
        ),
        "limit": (
            "இப்போதைக்கு செய்தி வரம்பை அடைந்துவிட்டீர்கள். மேலும் உதவிக்கு MWC உதவி எண் "
            "6536 2692 (24 மணி நேரம்) அழைக்கவும்."
        ),
        "change_language": "மொழியை மாற்று",
        "thanks": "நன்றி!",
    },
    "bn": {
        "emergency": "🚨 জরুরি অবস্থা? **995** (অ্যাম্বুলেন্স / ফায়ার সার্ভিস) অথবা **999** (পুলিশ) নম্বরে কল করুন।",
        "human": "মানুষের সাথে কথা বলতে চান? MWC হেল্পলাইন **6536 2692** (২৪ ঘণ্টা, প্রায় ১০টি ভাষা)।",
        "welcome": (
            "হ্যালো! সিঙ্গাপুরে বেতন, কাজের নিয়ম, নিরাপত্তা বা চিকিৎসা নিয়ে আমাকে প্রশ্ন করুন। "
            "আমি MOM এবং বিশ্বস্ত সংস্থার অফিসিয়াল তথ্য দিয়ে উত্তর দিই। "
            "আমি একটি ছাত্র প্রকল্প, MOM নই।\n\n"
            "আপনার নাম, কোম্পানির নাম বা FIN নম্বর শেয়ার করবেন না।"
        ),
        "placeholder": "আপনার প্রশ্ন লিখুন…",
        "error": (
            "দুঃখিত, কিছু একটা সমস্যা হয়েছে। আবার চেষ্টা করুন, অথবা MWC হেল্পলাইনে "
            "6536 2692 (২৪ ঘণ্টা) কল করুন।"
        ),
        "limit": (
            "আপাতত মেসেজের সীমা শেষ হয়েছে। আরও সাহায্যের জন্য MWC হেল্পলাইনে "
            "6536 2692 (২৪ ঘণ্টা) কল করুন।"
        ),
        "change_language": "ভাষা পরিবর্তন করুন",
        "thanks": "ধন্যবাদ!",
    },
}
