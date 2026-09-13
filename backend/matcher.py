import os
import json
import logging
from typing import List, Dict, Any, Tuple, Optional

# Load environment variables
from dotenv import load_dotenv
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
if os.path.exists(root_env):
    load_dotenv(root_env)
if os.path.exists(backend_env):
    load_dotenv(backend_env)
load_dotenv()

logger = logging.getLogger(__name__)

def apply_hard_filters(
    all_providers: List[Dict[str, Any]],
    category: str,
    max_budget: Optional[float] = None,
    availability_needed: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Step 3: Filter providers by hard constraints (category, budget, availability)
    before AI gets involved. Keep AI for judgment, not basic filtering.
    
    Returns:
        (passed_candidates, rejected_candidates_with_reasons)
    """
    passed = []
    rejected = []
    
    category_norm = (category or "").strip().lower()
    avail_norm = (availability_needed or "any").strip().lower()
    
    for p in all_providers:
        rejection_reasons = []
        
        # 1. Category check
        if category_norm and p["category"].lower() != category_norm:
            rejection_reasons.append(f"Category '{p['category']}' does not match requested '{category_norm}'")
        
        # 2. Budget constraint (hourly rate <= max budget)
        if max_budget is not None and max_budget > 0:
            if p["hourly_rate"] > max_budget:
                rejection_reasons.append(
                    f"Hourly rate (${p['hourly_rate']:.0f}/hr) exceeds max budget (${max_budget:.0f}/hr)"
                )
                
        # 3. Availability constraint
        if avail_norm and avail_norm not in ["any", "all", "flexible", ""]:
            p_avails = [a.lower() for a in p.get("availability_list", [])]
            # 'emergency' providers can handle almost anything
            has_avail = (avail_norm in p_avails) or ("emergency" in p_avails)
            if not has_avail:
                rejection_reasons.append(
                    f"Provider availability ({', '.join(p_avails)}) does not match '{avail_norm}'"
                )
        
        if rejection_reasons:
            p_copy = dict(p)
            p_copy["rejection_reasons"] = rejection_reasons
            rejected.append(p_copy)
        else:
            passed.append(p)
            
    return passed, rejected


def rank_with_heuristic(
    client_request: Dict[str, Any],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Intelligent heuristic fallback when no AI API key is provided, or as a baseline.
    Computes a match score based on keyword overlap between client description and provider skills/bio,
    combined with rating.
    """
    desc = (client_request.get("description", "") + " " + client_request.get("specific_needs", "")).lower()
    keywords = [w.strip() for w in desc.replace(",", " ").replace(".", " ").split() if len(w) > 3]
    
    ranked = []
    for p in candidates:
        text_corpus = (p["skills"] + " " + p["bio"] + " " + p.get("badge", "")).lower()
        keyword_hits = [w for w in keywords if w in text_corpus]
        
        # Base score from rating (4.5 -> 75, 5.0 -> 90)
        score = (p["rating"] / 5.0) * 80.0
        
        # Keyword relevance bonus
        score += min(len(keyword_hits) * 6.0, 18.0)
        
        # Years experience bonus
        score += min(p.get("years_experience", 5) * 0.5, 5.0)
        
        score = min(round(score, 1), 99.0)
        
        # Dynamic, human-like one-line reasoning based on provider profile and client query
        reason_parts = []
        if keyword_hits:
            reason_parts.append(f"Specializes in {keyword_hits[0]} matching your exact request")
        elif p.get("badge"):
            reason_parts.append(f"Recognized as a '{p['badge']}'")
        else:
            reason_parts.append(f"{p['years_experience']}+ years of proven trade expertise")
            
        reason_parts.append(f"with exceptional {p['rating']}★ rating from {p['review_count']} verified clients")
        
        reasoning = f"{p['name']} is a standout match: " + " ".join(reason_parts) + "."
        
        ranked.append({
            "provider_id": p["id"],
            "rank": 0, # set after sorting
            "match_score": score,
            "reasoning": reasoning,
            "highlighted_skills": p.get("skills_list", [])[:3],
            "provider": p
        })
        
    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    for idx, item in enumerate(ranked):
        item["rank"] = idx + 1
        
    return ranked


def rank_with_gemini(
    client_request: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    api_key: str
) -> List[Dict[str, Any]]:
    """
    Ranks candidates using Google Gemini API (gemini-2.5-flash via google-genai SDK).
    """
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    
    # Prepare minimal candidate summaries for token efficiency and crisp reasoning
    candidate_summaries = []
    for p in candidates:
        candidate_summaries.append({
            "id": p["id"],
            "name": p["name"],
            "hourly_rate": p["hourly_rate"],
            "rating": p["rating"],
            "reviews": p["review_count"],
            "skills": p["skills"],
            "bio": p["bio"],
            "badge": p.get("badge", ""),
            "years_experience": p.get("years_experience", 5)
        })
        
    prompt = f"""You are an expert AI service matching dispatcher.
A client has submitted the following service request:
- Category: {client_request.get('category')}
- Max Budget: ${client_request.get('max_budget', 'Flexible')}
- Timing/Availability Needed: {client_request.get('availability', 'Flexible')}
- Job Description & Requirements: "{client_request.get('description', '')}"

Here are the qualified service providers who have already passed the hard filter constraints:
{json.dumps(candidate_summaries, indent=2)}

Your task:
1. Rank all candidates from Best Match (Rank 1) downwards based on how well their specific expertise, bio, rating, and value align with the client's job requirements.
2. For each candidate, provide a punchy, persuasive ONE-LINE reason explaining why they are a strong match for this specific job.
3. Assign a match_score (integer between 70 and 99).
4. Select 2-3 most relevant highlighted_skills for each.

Return ONLY a valid JSON array of objects with this exact schema:
[
  {{
    "id": <provider_id>,
    "rank": <integer 1 to N>,
    "match_score": <integer 70-99>,
    "reasoning": "<one concise line explanation tailored to the client's request>",
    "highlighted_skills": ["skill1", "skill2"]
  }}
]
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    
    raw_text = response.text.strip()
    # Clean up json markdown fences if present
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    parsed = json.loads(raw_text.strip())
    
    # Map back to full candidate objects
    candidates_by_id = {p["id"]: p for p in candidates}
    ranked_results = []
    
    for item in parsed:
        p_id = item.get("id")
        if p_id in candidates_by_id:
            ranked_results.append({
                "provider_id": p_id,
                "rank": item.get("rank", len(ranked_results) + 1),
                "match_score": item.get("match_score", 85),
                "reasoning": item.get("reasoning", "Strong match for your requested service requirements."),
                "highlighted_skills": item.get("highlighted_skills", candidates_by_id[p_id].get("skills_list", [])[:3]),
                "provider": candidates_by_id[p_id]
            })
            
    # Include any candidate that might have been skipped by the LLM
    included_ids = {r["provider_id"] for r in ranked_results}
    for p in candidates:
        if p["id"] not in included_ids:
            ranked_results.append({
                "provider_id": p["id"],
                "rank": len(ranked_results) + 1,
                "match_score": 75,
                "reasoning": f"{p['name']} brings {p['rating']}★ quality and solid trade experience.",
                "highlighted_skills": p.get("skills_list", [])[:3],
                "provider": p
            })
            
    ranked_results.sort(key=lambda x: x["rank"])
    return ranked_results


def match_and_rank_providers(
    all_providers: List[Dict[str, Any]],
    client_request: Dict[str, Any],
    ai_preference: str = "auto"
) -> Dict[str, Any]:
    """
    End-to-end matching pipeline:
    1. Hard constraint filtering
    2. Gemini AI-powered ranking and 1-line reasoning (with smart heuristic fallback)
    3. Pipeline statistics for visualization
    """
    category = client_request.get("category", "")
    max_budget = client_request.get("max_budget")
    if max_budget is not None:
        try:
            max_budget = float(max_budget)
        except (ValueError, TypeError):
            max_budget = None
            
    availability = client_request.get("availability", "any")
    
    # Step 1: Hard filter
    passed_candidates, rejected_candidates = apply_hard_filters(
        all_providers=all_providers,
        category=category,
        max_budget=max_budget,
        availability_needed=availability
    )
    
    total_count = len(all_providers)
    passed_count = len(passed_candidates)
    rejected_count = len(rejected_candidates)
    
    if not passed_candidates:
        return {
            "status": "no_candidates",
            "message": "No providers met your hard constraints (budget, category, or availability). Try relaxing your budget or availability.",
            "pipeline": {
                "total_providers": total_count,
                "hard_filter_passed": passed_count,
                "hard_filter_rejected": rejected_count,
                "ai_provider_used": "none"
            },
            "ranked_matches": [],
            "rejected_candidates": rejected_candidates
        }
        
    # Step 2: Gemini AI Ranking
    gemini_key = os.getenv("GEMINI_API_KEY")
    ai_used = "Smart Heuristic Engine"
    ranked_matches = []
    
    target_ai = (ai_preference or "auto").lower()
    
    if target_ai in ["auto", "gemini"] and gemini_key:
        try:
            ranked_matches = rank_with_gemini(client_request, passed_candidates, gemini_key)
            ai_used = "Gemini AI Engine"
        except Exception as e:
            logger.warning(f"Gemini API call failed, falling back to heuristic: {e}")
            ranked_matches = rank_with_heuristic(client_request, passed_candidates)
            ai_used = f"Smart Heuristic Fallback (Gemini: {str(e)[:50]})"
    else:
        # Heuristic mode
        ranked_matches = rank_with_heuristic(client_request, passed_candidates)
        ai_used = "Smart Heuristic Engine (Offline)"
        
    return {
        "status": "success",
        "pipeline": {
            "total_providers": total_count,
            "hard_filter_passed": passed_count,
            "hard_filter_rejected": rejected_count,
            "ai_provider_used": ai_used
        },
        "ranked_matches": ranked_matches,
        "rejected_candidates": rejected_candidates
    }


