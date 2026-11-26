# Topics we search for on GitHub (temporary list, the team can change it)
"""GitHub topics we track, grouped by technology domain.

Each name must match a GitHub topic exactly (lowercase, hyphens, no spaces).
To track a new technology, add its topic to the right domain below.
"""

DOMAINS = {
    "Web": ["react", "vue", "angular", "svelte", "nextjs", "flask", "django", "fastapi"],
    "AI": ["pytorch", "tensorflow", "langchain", "llm", "scikit-learn"],
    "Mobile": ["flutter", "react-native", "android", "kotlin", "swift"],
    "Cyber": ["cybersecurity", "penetration-testing", "osint", "owasp", "vulnerability-scanner"],
    "Cloud": ["kubernetes", "docker", "terraform", "aws", "serverless"],
    "AR/VR": ["augmented-reality", "virtual-reality", "webxr", "unity", "openxr"],
    "Blockchain": ["ethereum", "solidity", "web3", "hardhat", "smart-contracts"],
    "Data": ["pandas", "apache-spark", "data-science", "dbt", "apache-airflow"],
    "IoT": ["iot", "arduino", "raspberry-pi", "mqtt", "esp32"],
}

# One flat list of every topic (no duplicates), used by the data collection code
ALL_TOPICS = []
for _topics in DOMAINS.values():
    for _topic in _topics:
        if _topic not in ALL_TOPICS:
            ALL_TOPICS.append(_topic)

# Real repos that carry a topic tag but are not about that technology
EXCLUDED_REPOS = {"morluto/rea"}