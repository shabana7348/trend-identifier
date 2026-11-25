import re

TECH_TAGS = {
    "react": {"web", "frontend", "beginner"},
    "vue": {"web", "frontend", "beginner", "fast"},
    "angular": {"web", "frontend", "enterprise"},
    "nextjs": {"web", "frontend", "fast"},
    "django": {"web", "backend", "beginner", "secure"},
    "flask": {"web", "backend", "beginner"},
    "nodejs": {"web", "backend", "fast"},
    "flutter": {"mobile", "beginner", "crossplatform"},
    "react-native": {"mobile", "crossplatform"},
    "kotlin": {"mobile", "android"},
    "swift": {"mobile", "ios"},
    "tensorflow": {"ai"},
    "pytorch": {"ai"},
    "langchain": {"ai", "chatbot"},
    "pandas": {"data", "beginner"},
    "docker": {"cloud", "deploy"},
    "kubernetes": {"cloud", "deploy", "scale"},
    "ethereum": {"blockchain"},
    "solidity": {"blockchain"},
    "arduino": {"iot", "hardware", "beginner"},
    "raspberry-pi": {"iot", "hardware", "beginner"},
    "esp32": {"iot", "hardware"},
    "unity": {"vr", "game"},
}

KEYWORD_TAGS = {
    "website": "web", "web": "web", "frontend": "frontend", "backend": "backend",
    "server": "backend", "phone": "mobile", "mobile": "mobile", "android": "android",
    "ios": "ios", "iphone": "ios", "crossplatform": "crossplatform",
    "beginner": "beginner", "easy": "beginner", "simple": "beginner",
    "fast": "fast", "quick": "fast", "ai": "ai", "ml": "ai", "chatbot": "chatbot",
    "data": "data", "analysis": "data", "secure": "secure", "security": "secure",
    "cloud": "cloud", "deploy": "deploy", "scale": "scale", "blockchain": "blockchain",
    "crypto": "blockchain", "sensor": "iot", "iot": "iot", "hardware": "hardware",
    "vr": "vr", "game": "game", "enterprise": "enterprise",
}


def extract_tags(description):
    """Turn free text into a set of tags using simple keyword matching."""
    tags = set()
    for word in re.findall(r"[a-z0-9]+", (description or "").lower()):
        for candidate in (word, word.rstrip("s")):
            if candidate in KEYWORD_TAGS:
                tags.add(KEYWORD_TAGS[candidate])
                break
    return tags


def recommend(description, growth_df, top_n=3):
    """Score = 10 points per matched tag + up to 10 bonus points for star growth."""
    tags = extract_tags(description)
    if not tags:
        return {"tags": [], "best": None, "runners_up": [],
                "message": "We couldn't recognise any needs in that description. Try words like web, mobile, AI or beginner."}

    growth_lookup = dict(zip(growth_df["technology"], growth_df["growth_pct"]))
    scored = []
    for tech, tech_tags in TECH_TAGS.items():
        matched = tags & tech_tags
        if not matched:
            continue
        growth = float(growth_lookup.get(tech, 0.0))
        score = len(matched) * 10 + max(min(growth, 20.0), 0.0) / 2
        scored.append({
            "technology": tech,
            "score": round(score, 1),
            "matched_tags": sorted(matched),
            "reason": f"{tech} matches {', '.join(sorted(matched))} and its repositories grew {growth:.1f}% in stars.",
        })

    scored.sort(key=lambda r: r["score"], reverse=True)
    if not scored:
        return {"tags": sorted(tags), "best": None, "runners_up": [],
                "message": "No technology in our list matches those needs yet."}
    return {"tags": sorted(tags), "best": scored[0], "runners_up": scored[1:top_n], "message": ""}