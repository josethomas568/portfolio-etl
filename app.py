import streamlit as st
import pandas as pd
import json
import os
import requests
import time
from datetime import datetime
import google.generativeai as genai

# --- CONSTANTS & CONFIG ---
DB_FILE = 'job_tracker.json'
THEME_COLORS = {
    "navy": "#0A192F",
    "slate": "#8892B0",
    "teal": "#64FFDA",
    "white": "#E6F1FF",
    "glass": "rgba(255, 255, 255, 0.05)"
}

st.set_page_config(page_title="Hired.AI | Portfolio Matcher", page_icon="🎯", layout="wide")

# --- CUSTOM UI ENGINE ---
def apply_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="st-"] {{
        font-family: 'Inter', sans-serif;
        color: {THEME_COLORS['white']};
    }}
    .stApp {{
        background-color: {THEME_COLORS['navy']};
    }}
    
    /* Section Headers */
    .section-header {{
        border-bottom: 2px solid {THEME_COLORS['teal']};
        padding-bottom: 10px;
        margin-bottom: 25px;
        color: {THEME_COLORS['teal']};
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {{ color: {THEME_COLORS['teal']}; font-weight: 800; }}
    [data-testid="stMetricLabel"] {{ color: {THEME_COLORS['slate']}; }}
    
    /* Glassmorphism Card */
    .glass-card {{
        background: {THEME_COLORS['glass']};
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-radius: 15px;
        padding: 25px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }}
    
    /* Portfolio Project Cards */
    .portfolio-card {{
        border-left: 4px solid {THEME_COLORS['teal']};
        background: rgba(136, 146, 176, 0.1);
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 10px 0;
    }}
    
    /* Sidebar Overrides */
    [data-testid="stSidebar"] {{
        background-color: #112240;
        border-right: 1px solid {THEME_COLORS['slate']};
    }}
    
    /* Button Styling */
    .stButton>button {{
        background-color: transparent;
        color: {THEME_COLORS['teal']};
        border: 1px solid {THEME_COLORS['teal']};
        border-radius: 5px;
        transition: all 0.3s;
    }}
    .stButton>button:hover {{
        background-color: rgba(100, 255, 218, 0.1);
        border: 1px solid {THEME_COLORS['teal']};
        transform: translateY(-2px);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- DATA PERSISTENCE LAYER ---
def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_to_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
    st.toast("Database Synchronized", icon="💾")

# --- API INTEGRATIONS ---
@st.cache_data(ttl=3600)
def fetch_github_data(username):
    url = f"https://api.github.com/users/{username}/repos?sort=updated"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return [{"name": r["name"], "desc": r["description"], "lang": r["language"], "url": r["html_url"]} for r in res.json()]
    except: return []
    return []

def get_best_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in ["models/gemini-1.5-flash", "gemini-1.5-flash"]:
            if m in models: return m
        return models[0] if models else None
    except: return "gemini-pro"

# --- CORE UI COMPONENTS ---
def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color:#64FFDA;'>Hired.AI</h2>", unsafe_allow_html=True)
        st.caption("Management Consulting Edition")
        st.divider()
        st.session_state.gh_user = st.text_input("GitHub Username", value=st.session_state.get('gh_user', ''))
        st.session_state.api_key = st.text_input("Gemini API Key", type="password")
        st.divider()
        st.markdown("### Guidance")
        st.info("Run `streamlit run app.py` to launch this dashboard locally.")

# --- MAIN APP LOGIC ---
def main():
    apply_custom_css()
    render_sidebar()
    
    # 1. Load and Prepare Data
    db_list = load_db()
    df = pd.DataFrame(db_list)
    
    # Global Metrics Calculation
    total_apps = len(db_list)
    interviews = len([x for x in db_list if x.get('Status') == 'Interviewing'])
    avg_match = sum([x.get('Match', 0) for x in db_list]) / total_apps if total_apps > 0 else 0

    # Layout: Metrics Header
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Applications", total_apps)
    m2.metric("Pipeline: Interviewing", interviews)
    m3.metric("Avg. Match Quality", f"{int(avg_match)}%")

    # Standardize Tab Names here
    tab_tracker, tab_matchmaker = st.tabs(["📊 PIPELINE TRACKER", "🎯 STRATEGIC MATCHER"])

    # --- TAB 1: TRACKER ---
    with tab_tracker:
        st.markdown('<div class="section-header">Application Pipeline</div>', unsafe_allow_html=True)
        
        # Glassmorphism Form
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("new_app", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 2, 1])
                comp = c1.text_input("Organization")
                role = c2.text_input("Designation")
                date_input = c3.date_input("Applied On")
                
                c4, c5 = st.columns([2, 1])
                status = c4.selectbox("Pipeline Status", ["Applied", "Interviewing", "Offered", "Rejected", "Archived"])
                match_val = c5.slider("Self-Assessed Match %", 0, 100, 50)
                
                if st.form_submit_button("Log Strategic Entry"):
                    if comp and role:
                        new_entry = {
                            "Company": comp,
                            "Role": role,
                            "Date": str(date_input),
                            "Status": status,
                            "Match": match_val
                        }
                        db_list.append(new_entry)
                        save_to_db(db_list)
                        st.rerun()
                    else:
                        st.error("Organization and Designation are required.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Advanced Data Grid
        if not df.empty:
            # FIX: Ensure the 'Date' column is converted to actual date objects for the UI
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date

            edited_df = st.data_editor(
                df,
                column_config={
                    "Match": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100, format="%d%%"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Applied", "Interviewing", "Offered", "Rejected", "Archived"]),
                    "Date": st.column_config.DateColumn("Applied Date", format="YYYY-MM-DD")
                },
                use_container_width=True,
                num_rows="dynamic",
                key="pipeline_editor"
            )
            
            if st.button("Commit Changes to Database"):
                # FIX: Convert back to string before saving to JSON
                final_df = edited_df.copy()
                if "Date" in final_df.columns:
                    final_df["Date"] = final_df["Date"].astype(str)
                save_to_db(final_df.to_dict('records'))
                st.rerun()
        else:
            st.info("No records found. Start by logging an application above.")

    # --- TAB 2: AI MATCHER ---
    with tab_matchmaker:
        st.markdown('<div class="section-header">Portfolio Alignment Engine</div>', unsafe_allow_html=True)
        
        col_in, col_out = st.columns([1, 1], gap="large")
        
        with col_in:
            st.markdown("### Opportunity Analysis")
            jd_text = st.text_area("Paste Target Job Description", height=400, placeholder="Identify core competencies...")
            analyze_btn = st.button("Execute Portfolio Analysis", type="primary", use_container_width=True)

        with col_out:
            st.markdown("### Tailored Output")
            if analyze_btn:
                if not st.session_state.get('api_key') or not st.session_state.get('gh_user'):
                    st.error("Missing Credentials in Sidebar")
                else:
                    with st.status("Initializing Strategic Match...", expanded=True) as status_box:
                        st.write("📡 Fetching GitHub Repositories...")
                        repos = fetch_github_data(st.session_state.gh_user)
                        
                        st.write("🧠 Contextualizing with Gemini 1.5...")
                        genai.configure(api_key=st.session_state.api_key)
                        model_name = get_best_model()
                        model = genai.GenerativeModel(model_name)
                        
                        prompt = f"Analyze these projects: {json.dumps(repos)} against this JD: {jd_text}. Select top 3. Return format: PROJECT: [Name] WHY: [Reason] BULLETS: [Bullets]"
                        
                        response = model.generate_content(prompt)
                        status_box.update(label="Analysis Complete!", state="complete", expanded=False)
                    
                    st.session_state.current_analysis = response.text
                    st.markdown(response.text)

                    st.download_button(
                        "📥 Export Strategy Brief (.md)",
                        data=response.text,
                        file_name=f"Strategy_Brief_{datetime.now().strftime('%Y%m%d')}.md",
                        use_container_width=True
                    )
            elif 'current_analysis' not in st.session_state:
                st.info("Awaiting input for strategic alignment...")

if __name__ == "__main__":
    main()
