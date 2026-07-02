import json
import re
import csv
import sys
from datetime import datetime

candidates_path = r"d:\D DRIVE DOWNLOADS\PROJECT - INDIARUNS\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl"
output_path = r"d:\D DRIVE DOWNLOADS\PROJECT - INDIARUNS\team_india_runs_founding_ai_engineer.csv"

# Define service/consulting companies (lowercase)
SERVICE_COMPANIES = {
    "tcs", "tataconsultancy", "tata consultancy services", "infosys", "wipro", 
    "accenture", "cognizant", "cognizant technology solutions", "capgemini", 
    "techmahindra", "tech mahindra", "l&t", "lnt", "larsen & toubro", "hcl", 
    "hcltech", "hcl technologies", "mindtree", "deloitte", "kpmg", "ey", 
    "ernst & young", "pwc", "pricewaterhousecoopers", "mckinsey", "boston consulting", 
    "bcg", "bain", "cts", "teleperformance", "genpact", "wns", "conduent", "syntel"
}

# Core ML/IR/Search skills
CORE_SKILLS = {
    "embeddings", "sentence-transformers", "openai embeddings", "bge", "e5", 
    "vector search", "semantic search", "retrieval", "hybrid search", "pinecone", 
    "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss", 
    "python", "ndcg", "mrr", "map", "evaluation frameworks", "a/b testing", 
    "ab testing", "information retrieval", "learning to rank", "learning-to-rank"
}

# Nice to have NLP/ML skills
NICE_SKILLS = {
    "llm fine-tuning", "fine-tuning llms", "lora", "qlora", "peft", "xgboost", 
    "nlp", "transformers", "pytorch", "tensorflow", "large language models", 
    "deep learning", "machine learning", "neural networks", "scikit-learn", 
    "huggingface", "bert", "gpt", "rag", "langchain", "llamaindex", "weights & biases",
    "mlflow", "databricks", "spark", "airflow", "gRPC"
}

# CV/Speech/Robotics skills (potential down-weight if no NLP/IR)
CV_SPEECH_ROBOTICS = {
    "computer vision", "opencv", "yolo", "cnn", "image classification", 
    "segmentation", "object detection", "speech recognition", "whisper", 
    "speech to text", "tts", "text to speech", "robotics", "ros", "cuda"
}

def is_honeypot(c):
    # 1. Expert/advanced skills with 0 months
    expert_zero_months = [s for s in c.get('skills', []) if s.get('proficiency') in ['expert', 'advanced'] and s.get('duration_months', 0) == 0]
    if len(expert_zero_months) >= 3:
        return True, f"Expert/Advanced skills with 0 months: {[s['name'] for s in expert_zero_months]}"
    
    # 2. Extreme experience discrepancy (e.g. profile vs career history)
    years_exp = c.get('profile', {}).get('years_of_experience', 0)
    career = c.get('career_history', [])
    total_duration_months = sum([job.get('duration_months', 0) for job in career])
    total_duration_years = total_duration_months / 12.0
    if years_exp > 0 and total_duration_years > 0:
        ratio = total_duration_years / years_exp
        if ratio > 3.0 or ratio < 0.25:
            return True, f"Extreme exp discrepancy: profile {years_exp} yrs, career {total_duration_years:.1f} yrs"
    
    # 3. Education start year > end year
    for edu in c.get('education', []):
        s_yr = edu.get('start_year')
        e_yr = edu.get('end_year')
        if s_yr and e_yr and s_yr > e_yr:
            return True, f"Education start year ({s_yr}) > end year ({e_yr})"
            
    # 4. Job start year > end year (or date inconsistency)
    for job in career:
        start = job.get('start_date')
        end = job.get('end_date')
        if start and end and start > end:
            return True, f"Job start date ({start}) after end date ({end})"
            
        desc = job.get('description', '')
        # Foundation date check
        found_match = re.search(r'founded\s+in\s+(\d{4})', desc, re.IGNORECASE)
        if found_match:
            founded_year = int(found_match.group(1))
            if start:
                start_year = int(start.split('-')[0])
                if start_year < founded_year:
                    return True, f"Job started in {start_year} before company founded in {founded_year}"

    return False, ""

def score_candidate(c):
    profile = c.get('profile', {})
    title_str = profile.get('current_title', 'Engineer')
    career = c.get('career_history', [])
    skills_list = c.get('skills', [])
    signals = c.get('redrob_signals', {})
    
    # 1. Experience Score (Ideal 5-9 years)
    years_exp = profile.get('years_of_experience', 0)
    if 5.0 <= years_exp <= 9.0:
        exp_score = 1.0
    elif 4.0 <= years_exp < 5.0:
        exp_score = 0.85
    elif 9.0 < years_exp <= 11.0:
        exp_score = 0.8
    elif 3.0 <= years_exp < 4.0:
        exp_score = 0.5
    elif 11.0 < years_exp <= 13.0:
        exp_score = 0.5
    else:
        exp_score = 0.1
        
    # 2. Location & Relocation Score
    # Noida/Pune preferred. Tier 1 cities: Noida, Pune, Delhi NCR, Mumbai, Hyderabad, Bangalore, Chennai, Kolkata.
    loc = profile.get('location', '').lower()
    country = profile.get('country', '').lower()
    willing_relocate = signals.get('willing_to_relocate', False)
    
    is_india = (country == "india") or ("india" in loc)
    is_pune_noida = "pune" in loc or "noida" in loc or "pune" in profile.get('summary', '').lower() or "noida" in profile.get('summary', '').lower()
    is_tier1 = any(city in loc for city in ["pune", "noida", "delhi", "ncr", "mumbai", "hyderabad", "bangalore", "bengaluru", "chennai", "kolkata"])
    
    if is_india:
        if is_pune_noida:
            loc_score = 1.0
        elif is_tier1:
            loc_score = 0.9 if willing_relocate else 0.8
        else:
            loc_score = 0.8 if willing_relocate else 0.5
    else:
        # Outside India
        loc_score = 0.2
        
    # 3. Consulting Firm Filter (Hard check)
    companies = [job.get('company', '').lower().strip() for job in career if job.get('company')]
    all_consulting = True
    has_product = False
    
    for comp in companies:
        is_svc = False
        for svc in SERVICE_COMPANIES:
            if svc in comp:
                is_svc = True
                break
        if not is_svc:
            has_product = True
            all_consulting = False
            
    if len(companies) > 0 and all_consulting:
        consulting_penalty = 0.05
    else:
        consulting_penalty = 1.0
        
    # 4. Pure Academic/Research Filter
    research_titles = ["research assistant", "phd", "postdoc", "academic", "professor", "lecturer", "fellow", "researcher", "intern"]
    all_research = True
    has_industry = False
    for job in career:
        title = job.get('title', '').lower()
        is_res = any(rt in title for rt in research_titles)
        if not is_res:
            has_industry = True
            all_research = False
            
    if len(career) > 0 and all_research:
        research_penalty = 0.1
    else:
        research_penalty = 1.0

    # 5. Out of coding practice check
    current_job = next((job for job in career if job.get('is_current')), None)
    out_of_coding = False
    if current_job:
        title = current_job.get('title', '').lower()
        is_managerial = any(m in title for m in ["manager", "director", "architect", "lead", "head"])
        if is_managerial and current_job.get('duration_months', 0) > 18:
            if signals.get('github_activity_score', -1) <= 5:
                out_of_coding = True
                
    coding_penalty = 0.6 if out_of_coding else 1.0

    # 6. Primary skills matching
    skills_prof_map = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    
    core_score = 0
    nice_score = 0
    cv_speech_score = 0
    
    core_matches = []
    nice_matches = []
    
    for s in skills_list:
        sname = s.get('name', '').lower()
        prof = s.get('proficiency', 'beginner')
        weight = skills_prof_map.get(prof, 1)
        dur = s.get('duration_months', 0)
        
        # Check core skills
        is_core = False
        for cs in CORE_SKILLS:
            if cs in sname:
                is_core = True
                break
        
        if is_core:
            core_score += weight * (dur + 6)
            core_matches.append(s.get('name'))
            continue
            
        # Check nice skills
        is_nice = False
        for ns in NICE_SKILLS:
            if ns in sname:
                is_nice = True
                break
        
        if is_nice:
            nice_score += weight * (dur + 6)
            nice_matches.append(s.get('name'))
            continue
            
        # Check CV/Speech
        is_cv = False
        for cvs in CV_SPEECH_ROBOTICS:
            if cvs in sname:
                is_cv = True
                break
        if is_cv:
            cv_speech_score += weight * (dur + 6)
            
    if cv_speech_score > 0 and core_score == 0 and nice_score < 10:
        cv_penalty = 0.1
    else:
        cv_penalty = 1.0

    # Strong LangChain wrapper filter
    has_wrapper = False
    has_traditional = False
    for s in skills_list:
        sname = s.get('name', '').lower()
        if "langchain" in sname or "openai" in sname or "chatgpt" in sname:
            has_wrapper = True
        if any(ts in sname for ts in ["pytorch", "tensorflow", "nlp", "information retrieval", "elasticsearch", "solr", "vector", "embedding", "scikit-learn"]):
            has_traditional = True
            
    if has_wrapper and not has_traditional and core_score < 10:
        wrapper_penalty = 0.2
    else:
        wrapper_penalty = 1.0

    # 7. Behavioral Signals Multiplier
    resp_rate = signals.get('recruiter_response_rate', 0.0)
    if resp_rate < 0.15:
        resp_mult = 0.4
    elif resp_rate < 0.35:
        resp_mult = 0.75
    else:
        resp_mult = 1.0
        
    # Activity
    last_act = signals.get('last_active_date', '2020-01-01')
    try:
        act_dt = datetime.strptime(last_act, "%Y-%m-%d")
        ref_dt = datetime(2026, 7, 2)
        days_inactive = (ref_dt - act_dt).days
    except:
        days_inactive = 365
        
    if days_inactive > 180: # 6 months
        act_mult = 0.15
    elif days_inactive > 90: # 3 months
        act_mult = 0.55
    elif days_inactive > 30: # 1 month
        act_mult = 0.85
    else:
        act_mult = 1.0
        
    # Notice Period
    notice = signals.get('notice_period_days', 90)
    if notice <= 30:
        notice_mult = 1.0
    elif notice <= 60:
        notice_mult = 0.85
    else:
        notice_mult = 0.5
        
    # Open to work
    otw = signals.get('open_to_work_flag', False)
    otw_mult = 1.0 if otw else 0.8
    
    # Interview completion rate
    int_comp = signals.get('interview_completion_rate', 1.0)
    int_mult = 1.0 if int_comp >= 0.7 else (0.5 if int_comp < 0.4 else 0.8)
    
    behavior_mult = resp_mult * act_mult * notice_mult * otw_mult * int_mult
    
    # 8. GitHub Activity Score
    gh_score = signals.get('github_activity_score', -1)
    if gh_score > 0:
        gh_mult = 1.0 + (gh_score / 150.0) # up to +66% boost for active GitHub
    else:
        gh_mult = 0.95
        
    # Calculate base matching score
    core_match_factor = min(core_score / 200.0, 1.0)
    nice_match_factor = min(nice_score / 300.0, 1.0)
    base_match = (core_match_factor * 0.6) + (nice_match_factor * 0.4)
    
    # Combine everything
    final_score = base_match * exp_score * loc_score * behavior_mult * gh_mult
    
    # Apply penalties
    final_score = final_score * consulting_penalty * research_penalty * coding_penalty * cv_penalty * wrapper_penalty
    
    final_score = max(0.0, min(1.0, final_score))
    
    # Generate reasoning - make sure it's 1-2 concise, highly specific sentences
    reasoning_parts = []
    reasoning_parts.append(f"AI Engineer with {years_exp:.1f} years experience, currently {title_str}.")
    
    if core_matches:
        core_str = ", ".join(core_matches[:3])
        reasoning_parts.append(f"Hands-on with search/retrieval tech like {core_str}.")
    
    loc_desc = "based in Noida/Pune" if is_pune_noida else f"based in {profile.get('location', 'India')}"
    notice_desc = f"{notice}-day notice"
    reasoning_parts.append(f"{loc_desc} ({notice_desc}).")
    
    if days_inactive < 30 and otw:
        reasoning_parts.append("Excellent active candidate profile views and response signals.")
        
    reasoning = " ".join(reasoning_parts)
    
    # Truncate reasoning to ensure it meets constraints (1-2 sentences)
    # Ensure there are no newlines in reasoning
    reasoning = reasoning.replace("\n", " ").replace("\r", "").strip()
    words = reasoning.split(" ")
    if len(words) > 30:
        reasoning = " ".join(words[:28]) + "..."
        
    return final_score, reasoning

def main():
    print("Loading candidates and starting ranking...")
    scored_candidates = []
    honeypot_count = 0
    scanned_count = 0
    
    with open(candidates_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            scanned_count += 1
            c = json.loads(line)
            cid = c.get('candidate_id')
            
            # Filter out honeypots immediately
            is_hp, reason = is_honeypot(c)
            if is_hp:
                honeypot_count += 1
                continue
                
            score, reasoning = score_candidate(c)
            scored_candidates.append({
                'candidate_id': cid,
                'score': score,
                'reasoning': reasoning
            })
            
            if scanned_count % 20000 == 0:
                print(f"Processed {scanned_count} candidates...")

    print(f"Total scanned: {scanned_count}")
    print(f"Total honeypots detected and filtered: {honeypot_count}")
    print(f"Candidates remaining for ranking: {len(scored_candidates)}")
    
    # Sort candidates:
    # Primary: score descending
    # Secondary: candidate_id ascending
    scored_candidates.sort(key=lambda x: (-x['score'], x['candidate_id']))
    
    # Select top 100
    top_100 = scored_candidates[:100]
    
    # Write to CSV
    with open(output_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['candidate_id', 'rank', 'score', 'reasoning'])
        for idx, cand in enumerate(top_100):
            writer.writerow([
                cand['candidate_id'],
                idx + 1, # rank 1-100
                round(cand['score'], 5), # round score to 5 decimals
                cand['reasoning']
            ])
            
    print(f"Finished writing top 100 to {output_path}")

if __name__ == '__main__':
    main()
