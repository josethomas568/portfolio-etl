# Portfolio ETL: AI-Powered Career Pipeline

A local, zero-dependency machine learning application and Streamlit dashboard designed to automate the extraction, transformation, and loading of job application data and portfolio alignment. 

By implementing an **LLM-driven matching strategy** using the Gemini 1.5 Flash model, this engine effectively bypasses the manual bottleneck of tailoring resumes, dynamically generating JD-specific STAR bullet points from live GitHub repository metadata.

## The Application Bottleneck
When applying for advanced data science and engineering roles, submitting a static, generalized resume results in low ATS matching scores. 

Traditional application pipelines require candidates to manually cross-reference their project history with job descriptions, rewrite bullet points to align with the company's specific tech stack (e.g., highlighting Spark streaming for one role, and XGBoost for another), and track the outcomes in disconnected spreadsheets. This creates a massive time deficit and reduces the volume of high-quality applications a candidate can submit.

## The LLM Transformation Strategy
To force a perfect alignment between a candidate's technical history and the target job, this architecture applies an Extract, Transform, Load (ETL) methodology to career management:

* **Extract:** The engine hits the GitHub REST API to pull down live repository names, descriptions, and primary languages.
* **Transform:** The Gemini inference engine cross-references the candidate's GitHub metadata against the pasted Job Description. It isolates the top two matching projects and dynamically generates tailored STAR-method bullet points utilizing the exact keywords found in the JD.
* **Load:** The final tailored outputs are formatted into a downloadable Markdown artifact, and the application metadata (Company, Role, Date, Status) is written to a local, secure flat-file database.

## Core Capabilities
Built to run completely locally, the application ensures 100% data privacy for the user's career tracker.

| Feature | Execution Strategy | Output |
| :--- | :--- | :--- |
| **Pipeline Tracking** | Flat-file JSON database | Dynamic Streamlit Dataframe |
| **Portfolio Sync** | `requests` to GitHub REST API | Cached repository metadata list |
| **AI Matchmaker** | Google GenAI SDK (Gemini 1.5 Flash) | JD-aligned project selection |
| **Resume Tailoring** | Zero-shot LLM prompting | Downloadable `.md` text stream |

---

## Tech Stack & Architecture
* **Frontend & Routing:** `streamlit`, `pandas`
* **Machine Learning / AI:** `google-genai` (Gemini 1.5 Flash)
* **Data Engineering:** `requests` (GitHub API), `json`, `os`
* **Local Infrastructure:** VS Code environment, local JSON storage

---

## Local Deployment & Execution
The application is designed as a standalone tool. It requires no external cloud databases and runs securely on localhost.

### Setup Instructions
You can initialize the engine using your local terminal:

```bash
# 1. Clone the repository
git clone [https://github.com/](https://github.com/)<YOUR-GITHUB-USERNAME>/portfolio-etl.git
cd portfolio-etl

# 2. Install dependencies
pip install streamlit google-genai requests pandas

# 3. Launch the Streamlit server
streamlit run app.py

Developed by Jose Thomas as a demonstration of LLM integration, automated data pipelines, and intelligent career management using Google AI Studio.
