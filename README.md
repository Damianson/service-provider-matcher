# 🛠️ Service-Provider Matcher

An AI-powered service matching platform combining **deterministic hard constraint business filtering** (budget, category, availability) with the **Gemini AI Engine** (Google Gemini) to deliver ranked, justified recommendations for home & professional service requests.

---

## 🏗️ Architecture & Matching Philosophy

```
  ┌────────────────────────────────────────────────────────┐
  │              Client Request (React Frontend)           │
  │  - Category: Plumber / Electrician / Cleaner / Tutor   │
  │  - Max Budget: $ / hr                                  │
  │  - Timing: Weekdays / Weekends / Evenings / Emergency  │
  │  - Nuanced Description: Free-form project details      │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │    Stage 1: Hard Constraint Filtering (Backend API)    │
  │  ✓ Exact Category Match                                │
  │  ✓ Provider Rate <= Max Budget                         │
  │  ✓ Availability Match (Emergency / Flexible / Days)    │
  │                                                        │
  │  * Keeps LLM for nuanced judgment, NOT basic filtering *│
  └──────────────────────────┬─────────────────────────────┘
                             │  (N Filtered Candidates)
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │     Stage 2: Gemini AI Engine Ranking & Reasoning      │
  │                 (Gemini 3.6 Flash)                     │
  │  ✓ Evaluates specific job requirements against skills  │
  │  ✓ Generates 1-line tailored justification per match   │
  │  ✓ Computes match fit percentage score (70% - 99%)     │
  └──────────────────────────┬─────────────────────────────┘
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │          Ranked Output Display (React UI)              │
  │  - #1 Best Match Badge + Ranked Provider Cards         │
  │  - Prominent "Why This Match" AI Reasoning Callout     │
  │  - Auditable "Excluded Candidates" Accordion           │
  └────────────────────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

- **Backend**: Python Flask 3.1, Flask-CORS, Gunicorn
- **Database**: SQLite with 20 realistic seeded service providers
- **Frontend**: React 19, Vite, Tailwind CSS, Lucide Icons
- **AI Layer**: **Gemini AI Engine** (`google-genai` SDK with `gemini-3.6-flash`) + Smart Heuristic Fallback
- **Deployment**: Multi-stage `Dockerfile` optimized for **GCP Cloud Run**

---

## 📦 Seeded Data Summary (20 Providers across 4 Categories)

| Category | Count | Rate Range | Sample Specialties |
|---|---|---|---|
| **Plumber** | 5 | \$45 – \$95/hr | 24/7 Emergency leaks, burst pipes, drain clearing, tankless heaters |
| **Electrician** | 5 | \$55 – \$110/hr | EV charger installs (Tesla Wall), smart home wiring, 200A panel upgrades |
| **Cleaner** | 5 | \$28 – \$60/hr | Eco-friendly botanicals, move-out deposit recovery, post-construction HEPA |
| **Tutor** | 5 | \$28 – \$70/hr | AP Calculus BC / STEM, SAT/ACT score booster, Python coding, ESL |

---

## 💻 Local Quickstart

### 1. Activate Environment & Start Backend

```bash
cd /mnt/c/Users/User/projects/service-provider-matcher
source venv/bin/activate

# Seed database
python backend/seed.py

# (Optional) Set your Gemini API key in .env or shell
export GEMINI_API_KEY="your-gemini-key"

# Run Flask API (Port 5000)
python backend/app.py
```

### 2. Start Frontend Dev Server

```bash
cd /mnt/c/Users/User/projects/service-provider-matcher/frontend
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## ☁️ Step 6: GCP Cloud Run Deployment

The project contains a production-ready multi-stage `Dockerfile` that compiles the React frontend and packages it directly into the Flask Gunicorn container.

### Deploying with Google Cloud SDK:

```bash
# 1. Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Deploy from source
gcloud run deploy service-provider-matcher \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --set-env-vars GEMINI_API_KEY=YOUR_KEY
```

Or run the automated script:
```bash
./deploy_cloudrun.sh
```

---

## 🧪 4 Demo Test Scenarios (Sanity Checks)

Use the built-in **Quick Test Scenarios** buttons in the UI or test via cURL:

### Test Request 1: 🚨 Urgent Burst Pipe (Plumber)
- **Category**: `plumber`
- **Budget**: `$100/hr`
- **Availability**: `emergency`
- **Description**: *"Water pipe bursting under kitchen sink, need immediate 24/7 response to prevent flooding."*
- **Expected Winner**: **Marcus Vance** (\$95/hr, 4.9⭐, 24/7 Emergency response, burst pipe specialist).

### Test Request 2: ⚡ EV Charger Installation (Electrician)
- **Category**: `electrician`
- **Budget**: `$95/hr`
- **Availability**: `weekends`
- **Description**: *"Need Level 2 Tesla Wall Connector installed in garage on a weekend."*
- **Expected Winner**: **Leo 'Spark' Zhang** (\$90/hr, 4.9⭐, EV & Smart Home Pro, hundreds of Wall Connector installs).

### Test Request 3: 🧹 Move-Out Deep Clean (Cleaner)
- **Category**: `cleaner`
- **Budget**: `$55/hr`
- **Availability**: `weekends`
- **Description**: *"End of lease move-out deep clean for apartment, oven interior and carpet steam to get security deposit back."*
- **Expected Winner**: **Viktor Hansen** (\$50/hr, 4.8⭐, Move-out deep clean & Deposit Back Guarantee).

### Test Request 4: 🎓 AP Calculus BC Prep (Tutor)
- **Category**: `tutor`
- **Budget**: `$60/hr`
- **Availability**: `evenings`
- **Description**: *"High school senior preparing for AP Calculus BC differential equations and integration techniques."*
- **Expected Winner**: **Dr. Aris Thorne** (\$55/hr, 5.0⭐, PhD in Applied Mathematics, 94% AP 5-star rate).

---