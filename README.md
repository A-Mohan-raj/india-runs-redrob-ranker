# Redrob Data & AI Challenge: Senior AI Engineer Candidate Ranker

This repository contains the candidate ranking engine built for the **Redrob AI Senior AI Engineer (Founding Team)** role Innovation Challenge in **INDIA.RUNS 2026**.

## Challenge Mandate

Given a pool of **100,000 candidates**, select and rank the **top 100** best-fit profiles. The system must run purely on CPU, with a 5-minute time limit, using a maximum of 16 GB RAM, and with **network off** during the ranking execution.

## Quick Start

### 1. Installation
Install the necessary dependency (fpdf2 for PDF generation only):
```bash
pip install fpdf2
```

### 2. Run the Candidate Ranker
Execute the ranking script. It processes the raw JSONL dataset, filters honeypot records, performs multi-criteria scoring, and writes the validated top-100 ranked CSV output:
```bash
python rank_candidates.py
```
*Output generated: `team_india_runs_founding_ai_engineer.csv`*

### 3. Validate Format Compliance
You can run the official validation script on the generated CSV file to confirm compliance:
```bash
python "[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" "team_india_runs_founding_ai_engineer.csv"
```

---

## Technical Approach & Filters

The candidate scoring model is a high-performance, multi-stage heuristic engine that translates the job description's nuances into numeric scores.

### 1. Robust Honeypot Detection
Our pre-processing step blocks synthetic candidates with impossible histories (relevance tier 0):
- **Skill Inconsistencies:** Disqualifies candidates claiming "expert" or "advanced" proficiency in 3+ skills with `duration_months == 0`.
- **Date Inconsistencies:** Filters out candidates with overlapping education years (start > end) or jobs started prior to the company's founding year.
- **Experience Discrepancy:** Flags candidates where years of experience in the profile deviates significantly (ratio >3x or <0.25x) from the sum of job durations in their career history.

### 2. Disqualifications & Penalties
- **Consulting/Service-only Resumes:** Resumes showing history *only* in large consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, etc.) are heavily penalized. Prior product company experience is required.
- **Academic-only Resumes:** Heavy penalty applied if all roles are purely academic or research (e.g. Ph.D. Researcher, Postdoc) without production shipping.
- **LangChain Demos / OpenAI Wrappers:** Candidates whose ML portfolio consists only of prompt-engineering tutorials are filtered unless they show pre-LLM ML experience.
- **Managerial Inactivity:** Down-weights candidates holding architect/director roles for >18 months who lack active GitHub activity (no production code contributions).

### 3. Core Match & Multipliers
- **Skill Match (60% Core / 40% Nice-to-Have):** Factors in proficiency level and duration. Requires core search/retrieval skills (vector DBs, dense/hybrid retrieval, python, A/B testing/evaluation frameworks like NDCG/MAP/MRR).
- **Experience Years:** Matches the optimal range of 5–9 years.
- **Location Alignment:** Noida/Pune (hybrid office sites) is highly favored, followed by Tier-1 cities (relocation willing).
- **Behavioral Signal Modifier:** Factors in active dates (recent activity within 30 days), sub-30-day notice periods, open-to-work flags, and historical response rates to ensure candidate availability.
- **GitHub Boost:** Amplifies the match score for active developer profiles (up to 66% boost).

---

## Performance Summary

- **Total Execution Time:** ~30 seconds for 100,000 candidate records.
- **RAM Consumption:** <50 MB (sequential file streaming).
- **Honeypots Caught:** 40 honeypot profiles successfully filtered.
- **Validator Status:** **PASSED** (100% compliant).
