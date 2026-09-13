import os
from database import init_db, get_db_connection, insert_provider

PROVIDERS = [
    # --- PLUMBERS (5) ---
    {
        "name": "Marcus Vance",
        "category": "plumber",
        "hourly_rate": 95.0,
        "rating": 4.9,
        "review_count": 128,
        "availability": "emergency,weekdays,weekends",
        "skills": "emergency leak repair,burst pipes,sump pump,water heater,boiler diagnosis",
        "bio": "15+ years master plumber specializing in high-urgency pipe failures and 24/7 rapid water mitigation.",
        "years_experience": 15,
        "badge": "24/7 Rapid Response"
    },
    {
        "name": "Elena Rostova",
        "category": "plumber",
        "hourly_rate": 45.0,
        "rating": 4.6,
        "review_count": 64,
        "availability": "weekdays",
        "skills": "faucet installation,drain clearing,toilet repair,minor pipe leaks",
        "bio": "Affordable neighborhood plumber offering honest pricing and dependable daytime plumbing maintenance.",
        "years_experience": 6,
        "badge": "Budget Friendly"
    },
    {
        "name": "Dave 'Wrench' Miller",
        "category": "plumber",
        "hourly_rate": 80.0,
        "rating": 4.8,
        "review_count": 92,
        "availability": "weekdays,weekends",
        "skills": "bathroom remodel,tankless water heaters,PEX repiping,fixture replacement",
        "bio": "Precision residential contractor known for neat installations, kitchen remodels, and modern tankless units.",
        "years_experience": 12,
        "badge": "Top Workmanship"
    },
    {
        "name": "Carlos Gomez",
        "category": "plumber",
        "hourly_rate": 65.0,
        "rating": 4.7,
        "review_count": 48,
        "availability": "evenings,weekends",
        "skills": "hydro jetting,camera sewer inspection,main line unclogging,garbage disposal",
        "bio": "Flexible after-hours drainage and sewer diagnostic technician equipped with fiber optic cameras.",
        "years_experience": 8,
        "badge": "Flexible Hours"
    },
    {
        "name": "Sarah Jenkins",
        "category": "plumber",
        "hourly_rate": 55.0,
        "rating": 4.8,
        "review_count": 75,
        "availability": "weekdays,evenings",
        "skills": "water filtration systems,reverse osmosis,low-flow toilets,eco fixtures",
        "bio": "Eco-conscious plumber dedicated to water conservation, filtration systems, and sustainable hardware.",
        "years_experience": 7,
        "badge": "Eco Specialist"
    },

    # --- ELECTRICIANS (5) ---
    {
        "name": "Leo 'Spark' Zhang",
        "category": "electrician",
        "hourly_rate": 90.0,
        "rating": 4.9,
        "review_count": 140,
        "availability": "weekdays,weekends",
        "skills": "EV charger installation,smart home automation,Tesla wall connector,Lutron lighting",
        "bio": "Certified clean energy and smart home electrical engineer with hundreds of Level 2 EV charging station installs.",
        "years_experience": 10,
        "badge": "EV & Smart Home Pro"
    },
    {
        "name": "Ray Campbell",
        "category": "electrician",
        "hourly_rate": 110.0,
        "rating": 4.8,
        "review_count": 86,
        "availability": "emergency,weekends,evenings",
        "skills": "power outage diagnosis,breaker tripping,emergency rewiring,hazard troubleshooting",
        "bio": "Licensed master electrician on call for urgent residential electrical failures and safety threats.",
        "years_experience": 16,
        "badge": "Emergency Callout"
    },
    {
        "name": "Priya Patel",
        "category": "electrician",
        "hourly_rate": 55.0,
        "rating": 4.7,
        "review_count": 52,
        "availability": "weekdays",
        "skills": "ceiling fan install,outlet replacement,GFCI protection,dimmer switches,recessed lighting",
        "bio": "Friendly, detail-oriented electrician focused on residential safety upgrades and aesthetic fixture lighting.",
        "years_experience": 5,
        "badge": "Great Value"
    },
    {
        "name": "Tom O'Connor",
        "category": "electrician",
        "hourly_rate": 100.0,
        "rating": 4.9,
        "review_count": 115,
        "availability": "weekdays",
        "skills": "200A panel upgrade,fuse box replacement,whole-home surge protection,generator transfer switch",
        "bio": "Specialist in main service panel upgrades, permits, and municipal code compliance for older homes.",
        "years_experience": 14,
        "badge": "Master Electrician"
    },
    {
        "name": "Anita Morales",
        "category": "electrician",
        "hourly_rate": 70.0,
        "rating": 4.6,
        "review_count": 39,
        "availability": "evenings,weekends",
        "skills": "landscape lighting,security camera wiring,outdoor GFCI,smart thermostats",
        "bio": "Evening and weekend specialist for smart security installations and outdoor architectural lighting.",
        "years_experience": 7,
        "badge": "Lighting Design"
    },

    # --- CLEANERS (5) ---
    {
        "name": "Amara Green Clean Team",
        "category": "cleaner",
        "hourly_rate": 45.0,
        "rating": 4.9,
        "review_count": 178,
        "availability": "weekdays,weekends",
        "skills": "eco-friendly cleaning,plant-based supplies,pet safe,allergy reduction,deep sanitation",
        "bio": "Hypoallergenic and pet-safe cleaning using 100% certified non-toxic biodegradable botanical solutions.",
        "years_experience": 8,
        "badge": "Top Rated Eco Clean"
    },
    {
        "name": "Viktor Hansen",
        "category": "cleaner",
        "hourly_rate": 50.0,
        "rating": 4.8,
        "review_count": 89,
        "availability": "weekends,emergency",
        "skills": "move-out deep clean,deposit recovery guarantee,oven interior,carpet steam cleaning,Airbnb turnover",
        "bio": "Rapid turnover specialist providing intense move-out and rental inspection cleaning with guarantee.",
        "years_experience": 6,
        "badge": "Deposit Back Guarantee"
    },
    {
        "name": "Maria Santos",
        "category": "cleaner",
        "hourly_rate": 28.0,
        "rating": 4.6,
        "review_count": 95,
        "availability": "weekdays",
        "skills": "standard house cleaning,dusting,vacuuming,kitchen sanitization,bathroom scrubbing",
        "bio": "Reliable recurring residential house cleaner with 10 years of loyal neighborhood clients.",
        "years_experience": 10,
        "badge": "Most Affordable"
    },
    {
        "name": "Jackson Heavy Duty Care",
        "category": "cleaner",
        "hourly_rate": 60.0,
        "rating": 4.7,
        "review_count": 61,
        "availability": "weekdays,weekends",
        "skills": "post-renovation dust removal,industrial steam,grout scrubbing,high window cleaning",
        "bio": "Equipped with commercial HEPA vacuums and heavy duty steamers for post-construction restoration.",
        "years_experience": 9,
        "badge": "Post-Construction Pro"
    },
    {
        "name": "Clara Dubois",
        "category": "cleaner",
        "hourly_rate": 40.0,
        "rating": 4.8,
        "review_count": 73,
        "availability": "weekdays,evenings",
        "skills": "home organization,closet decluttering,KonMari method,kitchen cabinet detailing",
        "bio": "Brings harmony and immaculate order to chaotic spaces with meticulous organizational systems.",
        "years_experience": 5,
        "badge": "Organization Whiz"
    },

    # --- TUTORS (5) ---
    {
        "name": "Dr. Aris Thorne",
        "category": "tutor",
        "hourly_rate": 55.0,
        "rating": 5.0,
        "review_count": 112,
        "availability": "weekends,evenings",
        "skills": "AP Calculus AB/BC,multivariable calculus,linear algebra,physics,differential equations",
        "bio": "PhD in Applied Mathematics with a proven record: 94% of AP students score a 5 on Calculus BC exams.",
        "years_experience": 11,
        "badge": "5-Star Math Mentor"
    },
    {
        "name": "Chloe Lin",
        "category": "tutor",
        "hourly_rate": 28.0,
        "rating": 4.7,
        "review_count": 44,
        "availability": "weekdays,weekends",
        "skills": "elementary math,pre-algebra,middle school science,homework helper,reading comprehension",
        "bio": "Patient, engaging educator who builds fundamental confidence and study habits in young learners.",
        "years_experience": 4,
        "badge": "Patient & Encouraging"
    },
    {
        "name": "Julian Sterling",
        "category": "tutor",
        "hourly_rate": 70.0,
        "rating": 4.9,
        "review_count": 130,
        "availability": "weekends,evenings",
        "skills": "SAT prep,ACT strategy,college admissions essays,Ivy League test prep,time management",
        "bio": "Specialized test prep strategist with average student score improvements of +190 SAT points.",
        "years_experience": 9,
        "badge": "Score Booster"
    },
    {
        "name": "Maya Al-Mansoor",
        "category": "tutor",
        "hourly_rate": 45.0,
        "rating": 4.8,
        "review_count": 68,
        "availability": "weekdays,evenings",
        "skills": "Python programming,AP Computer Science A,data structures,algorithms,web basics",
        "bio": "Software engineer and instructor passionate about teaching teens and adults how to code cleanly.",
        "years_experience": 6,
        "badge": "Coding Expert"
    },
    {
        "name": "Gabriel Navarro",
        "category": "tutor",
        "hourly_rate": 32.0,
        "rating": 4.7,
        "review_count": 55,
        "availability": "weekdays,weekends,evenings",
        "skills": "conversational Spanish,ESL English,grammar mastery,DELE exam prep,accent reduction",
        "bio": "Bilingual certified language tutor with fun, immersive methods for conversational and business fluency.",
        "years_experience": 7,
        "badge": "Bilingual Native"
    }
]

def seed():
    # Remove existing database if any to re-seed cleanly
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "providers.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"Removed old {db_file}")

    init_db(db_file)
    for p in PROVIDERS:
        insert_provider(p, db_file)

    print(f"Successfully seeded {len(PROVIDERS)} providers across 4 categories into SQLite database!")

if __name__ == "__main__":
    seed()

