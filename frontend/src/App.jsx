import React, { useState, useEffect } from 'react';
import {
  Wrench,
  Zap,
  Sparkles,
  GraduationCap,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Star,
  Layers,
  Cpu,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Info,
  Send,
  SlidersHorizontal,
  ThumbsUp,
  Briefcase
} from 'lucide-react';

const CATEGORIES = [
  { id: 'plumber', label: 'Plumber', icon: Wrench, color: 'from-blue-500 to-cyan-500', desc: 'Leaks, repiping, heaters & drains' },
  { id: 'electrician', label: 'Electrician', icon: Zap, color: 'from-amber-500 to-yellow-500', desc: 'Panels, EV chargers & smart wiring' },
  { id: 'cleaner', label: 'Cleaner', icon: Sparkles, color: 'from-emerald-500 to-teal-500', desc: 'Deep cleaning, move-outs & sanitization' },
  { id: 'tutor', label: 'Tutor', icon: GraduationCap, color: 'from-purple-500 to-indigo-500', desc: 'STEM, calculus, test prep & coding' }
];

const AVAILABILITY_OPTIONS = [
  { id: 'any', label: 'Flexible / Any' },
  { id: 'weekdays', label: 'Weekdays' },
  { id: 'weekends', label: 'Weekends' },
  { id: 'evenings', label: 'Evenings' },
  { id: 'emergency', label: 'Urgent / 24/7' }
];

const PRESETS = [
  {
    title: '🚨 Urgent Pipe Leak',
    category: 'plumber',
    budget: 100,
    availability: 'emergency',
    description: 'Emergency: Water pipe bursting under the kitchen sink, need someone who can respond immediately to prevent ceiling water damage.'
  },
  {
    title: '⚡ EV Charger Install',
    category: 'electrician',
    budget: 95,
    availability: 'weekends',
    description: 'Need a certified specialist to install a Level 2 Tesla Wall Connector in our 2-car garage on a weekend.'
  },
  {
    title: '🧹 Move-Out Deep Clean',
    category: 'cleaner',
    budget: 55,
    availability: 'weekends',
    description: 'End of lease move-out deep clean for a 2-bedroom apartment. Needs oven interior cleaning and carpet steam for deposit recovery.'
  },
  {
    title: '🎓 AP Calculus Prep',
    category: 'tutor',
    budget: 60,
    availability: 'evenings',
    description: 'High school senior looking for intensive tutoring in AP Calculus BC differential equations and integration techniques on weekday evenings.'
  }
];

export default function App() {
  const [category, setCategory] = useState('plumber');
  const [budget, setBudget] = useState(100);
  const [availability, setAvailability] = useState('any');
  const [description, setDescription] = useState('');
  const [aiPreference, setAiPreference] = useState('auto');

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [config, setConfig] = useState(null);
  const [showRejected, setShowRejected] = useState(false);
  const [showArch, setShowArch] = useState(false);
  const [bookedProvider, setBookedProvider] = useState(null);

  // Fetch config on mount
  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.log('API config check:', err));
  }, []);

  const handleApplyPreset = (preset) => {
    setCategory(preset.category);
    setBudget(preset.budget);
    setAvailability(preset.availability);
    setDescription(preset.description);
    setResults(null);
    setError(null);
  };

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category,
          max_budget: budget,
          availability,
          description,
          ai_preference: aiPreference
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to match providers');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      {/* Top Navbar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                Service-Provider Matcher
              </span>
              <div className="text-xs text-indigo-400 font-medium flex items-center gap-1.5">
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Hard Filter + AI Reasoning Pipeline
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* AI Engine Status Pill */}
            <div className="hidden sm:flex items-center gap-2 bg-slate-800/80 border border-slate-700/60 rounded-full px-3 py-1 text-xs text-slate-300">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Engine:</span>
              <select
                value={aiPreference}
                onChange={(e) => setAiPreference(e.target.value)}
                className="bg-transparent text-indigo-300 font-semibold focus:outline-none cursor-pointer"
              >
                <option value="auto" className="bg-slate-900 text-white">Gemini AI Engine (Active)</option>
                <option value="heuristic" className="bg-slate-900 text-white">Smart Heuristic Engine (Offline)</option>
              </select>
            </div>

            <button
              onClick={() => setShowArch(!showArch)}
              className="px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600 bg-slate-800/60 text-xs font-medium text-slate-300 hover:text-white transition flex items-center gap-1.5"
            >
              <Info className="w-3.5 h-3.5" />
              <span>Architecture</span>
            </button>
          </div>
        </div>
      </header>

      {/* Architecture Modal */}
      {showArch && (
        <div className="bg-slate-900/95 border-b border-indigo-500/20 px-6 py-6 transition">
          <div className="max-w-7xl mx-auto">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                System Architecture & Two-Stage Matching Flow
              </h3>
              <button
                onClick={() => setShowArch(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                Close ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
              <div className="bg-slate-950/70 border border-slate-800 p-3.5 rounded-xl">
                <span className="font-semibold text-blue-400 block mb-1">1. Seeded SQLite Database</span>
                20 verified realistic service providers across Plumber, Electrician, Cleaner, and Tutor categories with skills, rates, and verified ratings.
              </div>
              <div className="bg-slate-950/70 border border-slate-800 p-3.5 rounded-xl">
                <span className="font-semibold text-amber-400 block mb-1">2. Hard Constraint Filtering</span>
                Backend filters candidates by Category, Max Budget ($\le$ budget), and Availability before AI invocation. Guarantees deterministic business rules.
              </div>
              <div className="bg-slate-950/70 border border-slate-800 p-3.5 rounded-xl">
                <span className="font-semibold text-purple-400 block mb-1">3. AI Qualitative Reasoning</span>
                Gemini AI Engine receives client's freeform job description and qualified candidates to judge nuances and provide custom one-line justification per match.
              </div>
              <div className="bg-slate-950/70 border border-slate-800 p-3.5 rounded-xl">
                <span className="font-semibold text-emerald-400 block mb-1">4. Cloud Run Ready</span>
                Multi-stage container packaging Flask backend + built Vite React frontend into a unified, single-port Cloud Run microservice.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Form & Presets (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Quick Presets for Demo */}
          <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 glow-card">
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Quick Test Scenarios (Demo Presets)
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {PRESETS.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleApplyPreset(p)}
                  className="text-left px-3 py-2 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 hover:border-indigo-500/50 transition group"
                >
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-indigo-300">
                    {p.title}
                  </div>
                  <div className="text-[10px] text-slate-400 mt-0.5">
                    ${p.budget}/hr · {p.availability}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Request Form */}
          <form onSubmit={handleSearch} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 glow-card space-y-5">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-indigo-400" />
                Step 2: Service Request Form
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Configure your hard constraints and describe your job requirements.
              </p>
            </div>

            {/* 1. Category Picker */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2">
                1. Select Service Category <span className="text-rose-400">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {CATEGORIES.map((cat) => {
                  const Icon = cat.icon;
                  const isSelected = category === cat.id;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => setCategory(cat.id)}
                      className={`p-3 rounded-xl border text-left transition flex items-center gap-3 ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-950/40 text-white shadow-sm ring-1 ring-indigo-500/50'
                          : 'border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700 hover:bg-slate-800/40'
                      }`}
                    >
                      <div className={`p-2 rounded-lg bg-gradient-to-br ${cat.color} text-white shadow-sm`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-semibold">{cat.label}</div>
                        <div className="text-[10px] text-slate-400 leading-tight line-clamp-1">{cat.desc}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 2. Budget Range Slider */}
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                  2. Maximum Hourly Budget
                </label>
                <span className="text-sm font-bold text-emerald-400 font-mono bg-emerald-950/50 border border-emerald-800/50 px-2 py-0.5 rounded-lg">
                  ${budget}/hr
                </span>
              </div>
              <input
                type="range"
                min="25"
                max="130"
                step="5"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                <span>$25/hr (Economy)</span>
                <span>$75/hr (Standard)</span>
                <span>$130/hr (Master/Urgent)</span>
              </div>
            </div>

            {/* 3. Availability Selector */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-2 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-cyan-400" />
                3. Required Availability
              </label>
              <div className="flex flex-wrap gap-1.5">
                {AVAILABILITY_OPTIONS.map((opt) => {
                  const isSelected = availability === opt.id;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setAvailability(opt.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                        isSelected
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-slate-800/80 text-slate-300 hover:bg-slate-700/80 border border-slate-700/50'
                      }`}
                    >
                      {opt.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 4. Job Description / Nuanced Needs */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                4. Job Description & Details <span className="text-slate-500">(For AI Judgment)</span>
              </label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your exact issue, specific brands, urgency, or preferences (e.g., 'Water leaking under sink', 'Tesla Wall Connector 240V', 'KonMari organizer', 'Calculus exam next week')..."
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-xl font-semibold text-xs text-white shadow-lg transition flex items-center justify-center gap-2 ${
                loading
                  ? 'bg-indigo-700 cursor-not-allowed opacity-80'
                  : 'bg-gradient-to-r from-indigo-600 via-blue-600 to-indigo-600 hover:from-indigo-500 hover:to-blue-500 shadow-indigo-500/25 active:scale-[0.99]'
              }`}
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Executing Hard Filter & AI Ranking...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Run Matcher Pipeline</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Pipeline Status & Results (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-800/80 text-rose-200 text-xs flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block mb-0.5">Matching Error</span>
                {error}
              </div>
            </div>
          )}

          {/* Pipeline Visualizer (Always shown if results exist or during loading) */}
          {results && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 glow-card">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  Matching Pipeline Telemetry
                </span>
                <span className="text-xs font-mono text-indigo-400 bg-indigo-950/60 border border-indigo-800/50 px-2.5 py-0.5 rounded-full">
                  AI: {results.pipeline?.ai_provider_used || 'Active'}
                </span>
              </div>

              {/* 3 Step Visual Flow */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3">
                  <div className="text-slate-400 text-[11px]">Database Pool</div>
                  <div className="text-lg font-bold text-white mt-0.5">
                    {results.pipeline?.total_providers || 20}
                  </div>
                  <div className="text-[10px] text-slate-500">Total Seeded</div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3">
                  <div className="text-slate-400 text-[11px]">Hard Filter Passed</div>
                  <div className="text-lg font-bold text-emerald-400 mt-0.5">
                    {results.pipeline?.hard_filter_passed || 0}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    {results.pipeline?.hard_filter_rejected || 0} Excluded
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-3">
                  <div className="text-slate-400 text-[11px]">AI Ranked Output</div>
                  <div className="text-lg font-bold text-indigo-400 mt-0.5">
                    {results.ranked_matches?.length || 0}
                  </div>
                  <div className="text-[10px] text-slate-500">With 1-Line Reasons</div>
                </div>
              </div>
            </div>
          )}

          {/* Results List */}
          {results && results.ranked_matches && results.ranked_matches.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-indigo-400" />
                  Step 5: Ranked Provider Matches
                </h3>
                <span className="text-xs text-slate-400">
                  Ranked by AI qualitative fit & value
                </span>
              </div>

              <div className="space-y-4">
                {results.ranked_matches.map((item, index) => {
                  const p = item.provider;
                  const isFirst = index === 0;

                  return (
                    <div
                      key={p.id}
                      className={`rounded-2xl border p-5 transition glow-card relative overflow-hidden ${
                        isFirst
                          ? 'bg-gradient-to-b from-slate-900/90 to-slate-950 border-indigo-500/60 shadow-lg shadow-indigo-500/10'
                          : 'bg-slate-900/50 border-slate-800/80 hover:border-slate-700'
                      }`}
                    >
                      {/* Top Bar: Rank Badge + Score + Price */}
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div className="flex items-center gap-2.5">
                          <span
                            className={`px-2.5 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 ${
                              isFirst
                                ? 'bg-amber-500/20 border border-amber-500/40 text-amber-300'
                                : index === 1
                                ? 'bg-slate-700/50 border border-slate-600 text-slate-200'
                                : 'bg-slate-800/60 border border-slate-700/60 text-slate-300'
                            }`}
                          >
                            <Star className={`w-3.5 h-3.5 ${isFirst ? 'fill-amber-400 text-amber-400' : 'text-slate-400'}`} />
                            #{item.rank} {isFirst ? 'Best Match' : 'Match'}
                          </span>

                          <h4 className="text-base font-bold text-white">{p.name}</h4>

                          {p.badge && (
                            <span className="hidden sm:inline-block text-[11px] bg-indigo-950/60 border border-indigo-800/50 text-indigo-300 px-2 py-0.5 rounded-md font-medium">
                              {p.badge}
                            </span>
                          )}
                        </div>

                        <div className="text-right shrink-0">
                          <div className="text-base font-bold text-emerald-400 font-mono">
                            ${p.hourly_rate}
                            <span className="text-xs text-slate-400 font-normal">/hr</span>
                          </div>
                          <div className="text-[11px] text-slate-400 flex items-center justify-end gap-1">
                            <span className="text-amber-400 font-semibold">{p.rating}★</span>
                            <span>({p.review_count})</span>
                          </div>
                        </div>
                      </div>

                      {/* Prominent AI Reasoning Box (Step 4 & 5 Requirement) */}
                      <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-xl p-3.5 mb-3.5 flex items-start gap-3">
                        <div className="p-1.5 rounded-lg bg-indigo-600/30 text-indigo-300 shrink-0 mt-0.5">
                          <Sparkles className="w-4 h-4 text-indigo-300" />
                        </div>
                        <div>
                          <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-300 mb-0.5">
                            AI Match Reasoning
                          </div>
                          <p className="text-xs text-indigo-100 font-medium leading-relaxed">
                            {item.reasoning}
                          </p>
                        </div>
                      </div>

                      {/* Bio */}
                      <p className="text-xs text-slate-300 mb-3.5 line-clamp-2">
                        {p.bio}
                      </p>

                      {/* Skills & Availability Footer */}
                      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80 text-xs">
                        <div className="flex flex-wrap gap-1.5 items-center">
                          {p.skills_list?.slice(0, 3).map((skill, sIdx) => (
                            <span
                              key={sIdx}
                              className="px-2 py-0.5 rounded-md bg-slate-800/90 text-slate-300 text-[11px] border border-slate-700/50"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>

                        <div className="flex items-center gap-3">
                          <span className="text-[11px] text-slate-400 flex items-center gap-1">
                            <Clock className="w-3 h-3 text-cyan-400" />
                            {p.availability}
                          </span>

                          <button
                            onClick={() => setBookedProvider(p)}
                            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-200 hover:text-white font-medium text-xs transition flex items-center gap-1.5"
                          >
                            <Briefcase className="w-3.5 h-3.5" />
                            <span>Select</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* No Candidates Found */}
          {results && results.status === 'no_candidates' && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center glow-card">
              <div className="w-12 h-12 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto mb-3">
                <AlertCircle className="w-6 h-6 text-amber-400" />
              </div>
              <h4 className="text-base font-bold text-white mb-1">No Matches Passed Hard Filters</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
                {results.message}
              </p>
              <button
                type="button"
                onClick={() => {
                  setBudget(120);
                  setAvailability('any');
                }}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition"
              >
                Expand Budget & Availability
              </button>
            </div>
          )}

          {/* Disqualified Candidates Inspection (Step 3 Transparency) */}
          {results && results.rejected_candidates && results.rejected_candidates.length > 0 && (
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4">
              <button
                onClick={() => setShowRejected(!showRejected)}
                className="w-full flex items-center justify-between text-left text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
              >
                <span className="flex items-center gap-2">
                  <XCircle className="w-4 h-4 text-slate-500" />
                  Hard Filter Exclusions ({results.rejected_candidates.length} Providers Screened Out)
                </span>
                {showRejected ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showRejected && (
                <div className="mt-3 pt-3 border-t border-slate-800/60 space-y-2">
                  <p className="text-[11px] text-slate-500 mb-2">
                    These providers did not make it to the AI ranking layer because they failed your hard constraints:
                  </p>
                  {results.rejected_candidates.map((rp) => (
                    <div
                      key={rp.id}
                      className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-slate-300">{rp.name}</span>
                        <span className="text-[10px] text-slate-500 ml-2">(${rp.hourly_rate}/hr · {rp.category})</span>
                      </div>
                      <div className="text-[11px] text-rose-400 font-medium">
                        {rp.rejection_reasons?.[0] || 'Constraint not met'}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Initial State / Welcome Card */}
          {!results && !loading && (
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-10 text-center glow-card">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600/20 to-cyan-500/20 border border-indigo-500/30 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-indigo-400" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">
                Ready to Find Your Best Service Match
              </h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed mb-6">
                Choose a service category, specify your budget and timing, or click any of the quick demo presets on the left to watch the multi-stage matching pipeline in action.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-2 text-xs text-slate-400">
                <span className="px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60">
                  Step 1: 20 Fake Seeded Providers
                </span>
                <span className="px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60">
                  Step 2: Hard Filter Pre-screen
                </span>
                <span className="px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60">
                  Step 3: AI Ranked Reasoning
                </span>
              </div>
            </div>
          )}

        </div>
      </main>

      {/* Booking Confirmation Modal */}
      {bookedProvider && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-indigo-500/40 rounded-2xl p-6 max-w-md w-full glow-card shadow-2xl animate-in fade-in zoom-in-95">
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-lg font-bold text-white text-center mb-1">
              Provider Selected!
            </h3>
            <p className="text-xs text-slate-400 text-center mb-5">
              You selected <span className="text-white font-semibold">{bookedProvider.name}</span> for your {bookedProvider.category} service request.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs space-y-2 mb-6">
              <div className="flex justify-between">
                <span className="text-slate-400">Hourly Rate:</span>
                <span className="text-emerald-400 font-bold font-mono">${bookedProvider.hourly_rate}/hr</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Client Rating:</span>
                <span className="text-amber-400 font-semibold">{bookedProvider.rating}★ ({bookedProvider.review_count} reviews)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Availability:</span>
                <span className="text-cyan-400 font-medium">{bookedProvider.availability}</span>
              </div>
            </div>

            <button
              onClick={() => setBookedProvider(null)}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition"
            >
              Done
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        Service-Provider Matcher · Flask + SQLite + React + AI Layer · GCP Cloud Run Ready
      </footer>
    </div>
  );
}

