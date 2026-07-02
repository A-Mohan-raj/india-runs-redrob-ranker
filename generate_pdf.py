from fpdf import FPDF
import sys

class PDF(FPDF):
    def header(self):
        # Arial bold
        self.set_font('Helvetica', 'B', 15)
        # Title
        self.set_text_color(0, 51, 102) # Dark blue
        self.cell(0, 10, 'Redrob Data & AI Challenge - Submission Document', 0, 1, 'C')
        # Line break
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(filename="approach_explanation.pdf"):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Section
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "Intelligent Candidate Discovery & Ranking", 0, 1, 'C')
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(102, 102, 102)
    pdf.cell(0, 10, "IndiaRuns Hackathon 2026 | Team: IndiaRuns Founding AI Ranker", 0, 1, 'C')
    pdf.cell(0, 10, "Team Leader: Mohanraj", 0, 1, 'C')
    pdf.ln(10)
    
    # Divider line
    pdf.set_draw_color(0, 51, 102)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)
    
    # 1. Solution Overview
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "1. Solution Overview", 0, 1)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(0, 0, 0)
    
    overview_text = (
        "We built a high-performance, deterministic candidate matching and ranking system customized "
        "for the Senior AI Engineer (Founding Team) role at Redrob AI. The system rejects keyword-stuffing "
        "traps and filters out candidates with service-company-only backgrounds, pure academic profiles, "
        "or out-of-practice coding backgrounds. Crucially, it incorporates a comprehensive pre-processing "
        "honeypot detector that eliminates impossible synthetic candidate profiles (e.g. 8 years of experience "
        "at a company founded 3 years ago or expert proficiency with 0 years used), keeping the honeypot "
        "rate at 0% in the top 100."
    )
    pdf.multi_cell(0, 6, overview_text)
    pdf.ln(6)
    
    # 2. Key Requirements Extracted from JD
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "2. Job Description Understanding & Filters", 0, 1)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(102, 0, 0)
    pdf.cell(0, 6, "Positive Target Profile:", 0, 1)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(0, 0, 0)
    pos_targets = (
        "- Experience: Optimal range of 5-9 years in applied machine learning.\n"
        "- Location: Pune/Noida preferred (or Tier-1 cities like Hyderabad, Mumbai, Bangalore with relocation).\n"
        "- Core Skills: Production experience with embeddings (sentence-transformers, OpenAI), vector databases "
        "(Pinecone, Milvus, Qdrant, FAISS), and evaluation frameworks (NDCG, MAP, MRR).\n"
        "- GitHub Presence: High activity scores indicative of open-source contribution and active coding."
    )
    pdf.multi_cell(0, 6, pos_targets)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(102, 0, 0)
    pdf.cell(0, 6, "Active Disqualifiers & Penalties:", 0, 1)
    
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(0, 0, 0)
    neg_targets = (
        "- Service-only backgrounds: Candidates who only worked at consulting/service firms (TCS, Infosys, Wipro, "
        "Accenture, Cognizant, Capgemini, etc.) are heavily penalized.\n"
        "- Academic-only backgrounds: Ph.D./research-only candidates without industry shipping experience are filtered.\n"
        "- LangChain-only projects: Down-weights profiles with only recent generative wrappers but no traditional NLP/IR.\n"
        "- Out-of-coding practice: Senior roles (Manager/Director/Architect) with >18 months duration and low/no GitHub activity."
    )
    pdf.multi_cell(0, 6, neg_targets)
    pdf.ln(6)
    
    # 3. Ranking Methodology
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "3. Ranking & Scoring Methodology", 0, 1)
    pdf.ln(2)
    
    methodology = (
        "The final score is composed of multiple components, combined using a robust multiplicative formula:\n\n"
        "1. Base Match Score: Calculates semantic skill compatibility by weighting core skills (60%) and nice-to-have "
        "skills (40%), factoring in both proficiency levels (beginner to expert) and duration (months used).\n"
        "2. Experience Multiplier: Scores years of experience, peaking at 1.0 for 5-9 years and scaling down outside it.\n"
        "3. Location Multiplier: High weight for Pune/Noida, then Tier-1 cities willing to relocate, penalizing international.\n"
        "4. Behavioral Signals Modifier: Combines recruiter response rate, profile activity recency, notice period "
        "(sub-30 days highly preferred), open-to-work flag, and interview attendance.\n"
        "5. GitHub Booster: Active contributors get a score boost of up to 66% based on their github_activity_score.\n"
        "6. Tie-Breaking: Sorts candidates by score descending; exact ties are broken by candidate_id ascending."
    )
    pdf.multi_cell(0, 6, methodology)
    pdf.ln(6)
    
    # 4. Results & Verification
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 8, "4. System Performance & Constraints", 0, 1)
    pdf.ln(2)
    
    results = (
        "- Runtime: The entire 100,000 candidate pool is scanned, cleaned, and ranked in ~30 seconds.\n"
        "- Compute: Runs purely on a single CPU core, consuming less than 50MB of RAM via sequential streaming.\n"
        "- Network & GPU: Fully offline, no external API calls, satisfying all Stage 3 sandbox requirements.\n"
        "- Honeypots: Identified and filtered out 40 honeypot candidates. 0 honeypots reached the top 100 list.\n"
        "- Validation: Checked and validated using the official validate_submission.py validator (PASSED)."
    )
    pdf.multi_cell(0, 6, results)
    pdf.ln(10)
    
    # Sign off
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(102, 102, 102)
    pdf.cell(0, 6, "Built and validated successfully for the IndiaRuns 2026 Hackathon.", 0, 1, 'C')
    
    # Save the file
    pdf.output(filename)
    print(f"PDF successfully generated: {filename}")

if __name__ == '__main__':
    create_pdf()
