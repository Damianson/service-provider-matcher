import urllib.request
import json
import time

scenarios = [
    {
        "name": "1. 🚨 Urgent Pipe Leak",
        "payload": {
            "category": "plumber",
            "max_budget": 100,
            "availability": "emergency",
            "description": "Pipe burst under sink, urgent water mitigation needed!"
        }
    },
    {
        "name": "2. ⚡ EV Charger Installation",
        "payload": {
            "category": "electrician",
            "max_budget": 95,
            "availability": "weekends",
            "description": "Need Level 2 Tesla Wall Connector installed in garage."
        }
    },
    {
        "name": "3. 🧹 Move-out Deep Clean",
        "payload": {
            "category": "cleaner",
            "max_budget": 55,
            "availability": "weekends",
            "description": "Move out inspection cleaning, oven interior and carpet steam."
        }
    },
    {
        "name": "4. 🎓 AP Calculus BC Tutor",
        "payload": {
            "category": "tutor",
            "max_budget": 60,
            "availability": "evenings",
            "description": "AP Calculus BC differential equations and test prep."
        }
    }
]

print("=================================================================")
print(" SANITY-CHECK: TESTING 4 DEMO SCENARIOS AGAINST MATCHING PIPELINE")
print("=================================================================\n")

for s in scenarios:
    req = urllib.request.Request(
        "http://127.0.0.1:5000/api/match",
        data=json.dumps(s["payload"]).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))

    pipe = data["pipeline"]
    top = data["ranked_matches"][0]
    p = top["provider"]

    print(f"Scenario: {s['name']}")
    print(f"Request:  Category={s['payload']['category']}, Budget=${s['payload']['max_budget']}/hr, Timing={s['payload']['availability']}")
    print(f"Pipeline: Total={pipe['total_providers']} | Hard-Filter Passed={pipe['hard_filter_passed']} | Disqualified={pipe['hard_filter_rejected']}")
    print(f"AI Engine: {pipe['ai_provider_used']}")
    print(f"Winner:   #{top['rank']} {p['name']} (${p['hourly_rate']}/hr, {p['rating']}★, {p.get('badge')})")
    print(f"Reason:   \"{top['reasoning']}\"")
    print(f"Skills:   {', '.join(top['highlighted_skills'])}")
    print("-" * 65)
    time.sleep(1)

