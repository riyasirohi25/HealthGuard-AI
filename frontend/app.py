import streamlit as st
import requests
import time
import json

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HealthGuard AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

/* ── Root Variables ── */
:root {
    --electric-blue: #00d4ff;
    --electric-green: #00ff88;
    --deep-blue: #001a2e;
    --mid-blue: #002d4a;
    --card-bg: rgba(0, 30, 60, 0.7);
    --glow-blue: 0 0 20px rgba(0, 212, 255, 0.4);
    --glow-green: 0 0 20px rgba(0, 255, 136, 0.4);
    --text-main: #e0f4ff;
    --text-dim: #7ab8cc;
    --border-glow: rgba(0, 212, 255, 0.2);
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background: #000d1a;
    color: var(--text-main);
}

/* ── Animated Background ── */
.stApp {
    background: 
        radial-gradient(ellipse at 10% 20%, rgba(0, 100, 200, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(0, 200, 100, 0.1) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(0, 30, 80, 0.8) 0%, transparent 70%),
        #000d1a;
    min-height: 100vh;
}

/* ── Hide Streamlit Defaults ── */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000d1a 0%, #001a30 100%);
    border-right: 1px solid var(--border-glow);
    box-shadow: 4px 0 30px rgba(0, 212, 255, 0.05);
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: var(--text-dim) !important;
    font-family: 'Exo 2', sans-serif;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-glow) !important;
    color: var(--electric-blue) !important;
    font-family: 'Exo 2', sans-serif;
}

/* ── Text Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
textarea {
    background: rgba(0, 20, 50, 0.8) !important;
    border: 1px solid var(--border-glow) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    font-family: 'Exo 2', sans-serif !important;
    transition: all 0.3s ease;
}

[data-testid="stTextInput"] input:focus,
textarea:focus {
    border-color: var(--electric-blue) !important;
    box-shadow: var(--glow-blue) !important;
    outline: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 255, 136, 0.1));
    border: 1px solid var(--electric-blue);
    color: var(--electric-blue);
    font-family: 'Orbitron', monospace;
    font-weight: 700;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.6rem 1.8rem;
    border-radius: 4px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.3), rgba(0, 255, 136, 0.2));
    box-shadow: var(--glow-blue), inset 0 0 20px rgba(0, 212, 255, 0.1);
    transform: translateY(-2px);
    color: #ffffff;
    border-color: var(--electric-green);
}

.stButton > button:active {
    transform: translateY(0px);
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--card-bg);
    border: 1px solid var(--border-glow);
    border-radius: 12px;
    padding: 1rem;
    backdrop-filter: blur(10px);
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--electric-green) !important;
    font-family: 'Orbitron', monospace;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: var(--card-bg);
    border: 1px solid var(--border-glow);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #000d1a; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--electric-blue), var(--electric-green));
    border-radius: 2px;
}

/* ── Animations ── */
@keyframes pulse-glow {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

@keyframes slide-in-left {
    from { transform: translateX(-30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slide-in-up {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

@keyframes scan-line {
    0% { top: -5%; }
    100% { top: 105%; }
}

@keyframes border-flow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ── Custom Components ── */
.hg-hero {
    animation: slide-in-up 0.8s ease;
    text-align: center;
    padding: 2rem 0 1.5rem;
    position: relative;
}

.hg-title {
    font-family: 'Orbitron', monospace;
    font-size: 3.2rem;
    font-weight: 900;
    background: linear-gradient(90deg, var(--electric-blue), var(--electric-green), var(--electric-blue));
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: border-flow 4s ease infinite;
    letter-spacing: 4px;
    line-height: 1.1;
    margin: 0;
}

.hg-subtitle {
    font-family: 'Exo 2', sans-serif;
    color: var(--text-dim);
    font-size: 0.95rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.5rem;
    animation: pulse-glow 3s ease infinite;
}

.hg-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--electric-blue), var(--electric-green), transparent);
    margin: 1.5rem 0;
    animation: border-flow 3s ease infinite;
    background-size: 200% auto;
}

.hg-card {
    background: var(--card-bg);
    border: 1px solid var(--border-glow);
    border-radius: 16px;
    padding: 1.8rem;
    backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    animation: slide-in-up 0.5s ease;
    transition: all 0.3s ease;
}

.hg-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--electric-blue), var(--electric-green), transparent);
}

.hg-card:hover {
    border-color: rgba(0, 212, 255, 0.5);
    box-shadow: var(--glow-blue);
    transform: translateY(-3px);
}

.hg-section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    color: var(--electric-blue);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.hg-label {
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.3rem;
}

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.8rem;
    border-radius: 20px;
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    font-weight: 700;
}

.badge-normal { 
    background: rgba(0, 255, 136, 0.15);
    border: 1px solid var(--electric-green);
    color: var(--electric-green);
    text-shadow: var(--glow-green);
}

.badge-high { 
    background: rgba(255, 100, 50, 0.15);
    border: 1px solid #ff6432;
    color: #ff6432;
}

.badge-low { 
    background: rgba(255, 200, 0, 0.15);
    border: 1px solid #ffcc00;
    color: #ffcc00;
}

.badge-critical { 
    background: rgba(255, 0, 60, 0.2);
    border: 1px solid #ff003c;
    color: #ff003c;
    animation: pulse-glow 1s ease infinite;
}

.result-card {
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-left: 3px solid var(--electric-blue);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    animation: slide-in-left 0.4s ease;
}

.result-card-green {
    background: rgba(0, 255, 136, 0.05);
    border: 1px solid rgba(0, 255, 136, 0.2);
    border-left: 3px solid var(--electric-green);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    animation: slide-in-left 0.4s ease;
}

.confidence-bar-container {
    background: rgba(0, 20, 50, 0.8);
    border: 1px solid var(--border-glow);
    border-radius: 20px;
    height: 8px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, var(--electric-blue), var(--electric-green));
    box-shadow: var(--glow-blue);
    transition: width 1s ease;
}

.scan-container {
    position: relative;
    overflow: hidden;
}

.disclaimer-box {
    background: rgba(255, 150, 0, 0.08);
    border: 1px solid rgba(255, 150, 0, 0.3);
    border-left: 3px solid #ff9600;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    font-size: 0.8rem;
    color: rgba(255, 150, 0, 0.9);
    letter-spacing: 0.5px;
}

.sidebar-logo {
    font-family: 'Orbitron', monospace;
    font-size: 1.1rem;
    font-weight: 900;
    background: linear-gradient(90deg, var(--electric-blue), var(--electric-green));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 2px;
    text-align: center;
    padding: 1rem 0;
}

.nav-hint {
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-dim);
    text-align: center;
    padding-bottom: 0.5rem;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1rem 0;
}

.stat-item {
    background: rgba(0, 20, 50, 0.6);
    border: 1px solid var(--border-glow);
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
}

.stat-num {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--electric-green);
}

.stat-label {
    font-size: 0.6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 0.2rem;
}

.module-card {
    background: var(--card-bg);
    border: 1px solid var(--border-glow);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.module-card:hover {
    border-color: var(--electric-blue);
    box-shadow: var(--glow-blue);
    transform: translateY(-5px);
}

.module-icon {
    font-size: 2.5rem;
    margin-bottom: 0.8rem;
}

.module-name {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: var(--electric-blue);
    text-transform: uppercase;
}

.module-desc {
    font-size: 0.75rem;
    color: var(--text-dim);
    margin-top: 0.3rem;
}

.typing-cursor {
    display: inline-block;
    width: 2px;
    height: 1em;
    background: var(--electric-blue);
    animation: pulse-glow 0.8s ease infinite;
    vertical-align: text-bottom;
    margin-left: 2px;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: make API call with error handling ────────────────────────────────
def api_call(endpoint, payload):
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=5)
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "backend_offline"
    except Exception as e:
        return None, str(e)

def api_status():
    try:
        r = requests.get(f"{API_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">⚡ HEALTHGUARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-hint">Select Module</div>', unsafe_allow_html=True)

    page = st.selectbox(
        "",
        ["🏠  Home", "🧬  Disease Predictor", "🔬  Lab Analyzer", "💬  Medical Q&A", "📄  OCR Scanner"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    # API Status indicator
    online = api_status()
    status_color = "#00ff88" if online else "#ff6432"
    status_text = "ONLINE" if online else "OFFLINE"
    st.markdown(f"""
    <div style="text-align:center; padding: 0.5rem;">
        <div style="display:inline-flex; align-items:center; gap:8px;
                    background:rgba(0,20,50,0.6); border:1px solid {status_color}33;
                    border-radius:20px; padding:0.4rem 1rem;">
            <div style="width:8px;height:8px;border-radius:50%;
                        background:{status_color};
                        box-shadow:0 0 8px {status_color};
                        {'animation:pulse-glow 1s ease infinite' if online else ''}">
            </div>
            <span style="font-family:'Orbitron',monospace;font-size:0.6rem;
                         letter-spacing:2px;color:{status_color};">
                API {status_text}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.65rem;color:rgba(122,184,204,0.5);
                text-align:center;letter-spacing:1px;padding:0.5rem;">
        HealthGuard AI v0.1.0<br>
        <span style="color:rgba(0,255,136,0.4);">Self-hosted · No external APIs</span>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if "Home" in page:
    st.markdown("""
    <div class="hg-hero">
        <div class="hg-title">HEALTHGUARD AI</div>
        <div class="hg-subtitle">⚡ Intelligent Medical Analysis System · Fully Self-Hosted</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div class="stat-grid">
        <div class="stat-item">
            <div class="stat-num">41</div>
            <div class="stat-label">Diseases</div>
        </div>
        <div class="stat-item">
            <div class="stat-num" style="color:var(--electric-blue);">47K+</div>
            <div class="stat-label">QA Pairs</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">0</div>
            <div class="stat-label">Ext. APIs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    # Module cards
    col1, col2, col3, col4 = st.columns(4)
    modules = [
        ("🧬", "Disease Predictor", "Symptoms → Conditions"),
        ("🔬", "Lab Analyzer", "Values → Interpretation"),
        ("💬", "Medical Q&A", "Questions → Answers"),
        ("📄", "OCR Scanner", "Reports → Text"),
    ]
    for col, (icon, name, desc) in zip([col1, col2, col3, col4], modules):
        with col:
            st.markdown(f"""
            <div class="module-card">
                <div class="module-icon">{icon}</div>
                <div class="module-name">{name}</div>
                <div class="module-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    # How it works
    st.markdown('<div class="hg-section-title">How It Works</div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    steps = [
        ("01", "INPUT", "Enter symptoms, lab values, or ask a question"),
        ("02", "ANALYZE", "AI processes using trained BioBERT + RAG models"),
        ("03", "EXPLAIN", "Get structured insights in plain language"),
    ]
    for col, (num, title, desc) in zip([c1, c2, c3], steps):
        with col:
            st.markdown(f"""
            <div class="hg-card" style="text-align:center;">
                <div style="font-family:'Orbitron',monospace;font-size:2rem;
                            color:var(--electric-blue);opacity:0.3;font-weight:900;">
                    {num}
                </div>
                <div style="font-family:'Orbitron',monospace;font-size:0.8rem;
                            letter-spacing:3px;color:var(--electric-green);margin:0.5rem 0;">
                    {title}
                </div>
                <div style="font-size:0.8rem;color:var(--text-dim);">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer-box">
        ⚠ DISCLAIMER — HealthGuard AI is a research and support tool only.
        It does not replace professional medical advice, diagnosis, or treatment.
        Always consult a qualified healthcare provider.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DISEASE PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Disease" in page:
    st.markdown("""
    <div class="hg-hero" style="text-align:left;padding:1rem 0;">
        <div class="hg-section-title">🧬 Disease Predictor</div>
        <div style="font-size:0.8rem;color:var(--text-dim);letter-spacing:1px;margin-top:0.3rem;">
            Describe your symptoms — AI maps them to possible conditions
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="hg-label">Enter Symptoms</div>', unsafe_allow_html=True)
        symptoms = st.text_area(
            "",
            placeholder="e.g. fever, headache, sore throat, fatigue, body ache...",
            height=140,
            label_visibility="collapsed"
        )

        st.markdown('<div class="hg-label" style="margin-top:1rem;">Additional Context (optional)</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=1, max_value=120, value=25, label_visibility="visible")
        with c2:
            sex = st.selectbox("Biological Sex", ["Not specified", "Male", "Female"])

        duration = st.select_slider(
            "Symptom Duration",
            options=["< 1 day", "1-3 days", "3-7 days", "1-2 weeks", "> 2 weeks"],
            value="1-3 days"
        )

        analyze_btn = st.button("⚡  ANALYZE SYMPTOMS", use_container_width=True)

    with col_result:
        if analyze_btn:
            if not symptoms.strip():
                st.markdown("""
                <div class="result-card" style="border-left-color:#ff6432;">
                    <span style="color:#ff6432;font-family:'Orbitron',monospace;
                                 font-size:0.75rem;letter-spacing:2px;">
                        ⚠ INPUT REQUIRED
                    </span>
                    <p style="color:var(--text-dim);font-size:0.8rem;margin-top:0.5rem;">
                        Please describe your symptoms before analyzing.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                with st.spinner(""):
                    st.markdown("""
                    <div style="text-align:center;padding:2rem;color:var(--electric-blue);
                                font-family:'Orbitron',monospace;font-size:0.75rem;
                                letter-spacing:3px;animation:pulse-glow 1s infinite;">
                        ⚡ SCANNING NEURAL PATHWAYS...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1.5)

                data, err = api_call("/predict/disease", {
                    "text": symptoms,
                    "age": age,
                    "sex": sex.lower(),
                    "duration": duration
                })

                if err == "backend_offline":
                    # Demo mode
                    st.markdown("""
                    <div style="font-family:'Orbitron',monospace;font-size:0.6rem;
                                letter-spacing:2px;color:#ffcc00;margin-bottom:1rem;">
                        ⚠ DEMO MODE — Backend not connected
                    </div>
                    """, unsafe_allow_html=True)

                    demo_results = [
                        {"disease": "Common Cold", "confidence": 0.78},
                        {"disease": "Influenza (Flu)", "confidence": 0.61},
                        {"disease": "Viral Pharyngitis", "confidence": 0.43},
                    ]
                    st.markdown('<div class="hg-label">ANALYSIS RESULTS</div>', unsafe_allow_html=True)

                    for i, item in enumerate(demo_results):
                        conf_pct = int(item["confidence"] * 100)
                        color = "var(--electric-green)" if i == 0 else "var(--electric-blue)"
                        st.markdown(f"""
                        <div class="result-card" style="border-left-color:{color}">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="font-family:'Orbitron',monospace;
                                             font-size:0.8rem;color:{color};">
                                    {item['disease']}
                                </span>
                                <span style="font-family:'Orbitron',monospace;
                                             font-size:0.75rem;color:{color};">
                                    {conf_pct}%
                                </span>
                            </div>
                            <div class="confidence-bar-container" style="margin-top:0.6rem;">
                                <div class="confidence-bar-fill" style="width:{conf_pct}%;
                                     background:linear-gradient(90deg,{color},{color}88);">
                                </div>
                            </div>
                            <div style="font-size:0.7rem;color:var(--text-dim);margin-top:0.4rem;">
                                Confidence Score
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("""
                    <div class="disclaimer-box" style="margin-top:1rem;">
                        Results are probabilistic predictions, not diagnoses.
                        Consult a doctor for proper evaluation.
                    </div>
                    """, unsafe_allow_html=True)

                elif data:
                    st.markdown('<div class="hg-label">ANALYSIS RESULTS</div>', unsafe_allow_html=True)
                    diseases = data.get("diseases", [])
                    for i, item in enumerate(diseases[:3]):
                        conf = item.get("confidence", 0)
                        conf_pct = int(conf * 100)
                        color = "var(--electric-green)" if i == 0 else "var(--electric-blue)"
                        st.markdown(f"""
                        <div class="result-card">
                            <div style="display:flex;justify-content:space-between;">
                                <span style="font-family:'Orbitron',monospace;
                                             font-size:0.8rem;color:{color};">
                                    {item.get('disease','Unknown')}
                                </span>
                                <span style="font-family:'Orbitron',monospace;
                                             color:{color};">{conf_pct}%</span>
                            </div>
                            <div class="confidence-bar-container" style="margin-top:0.6rem;">
                                <div class="confidence-bar-fill" style="width:{conf_pct}%"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:200px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed rgba(0,212,255,0.15);border-radius:12px;
                        flex-direction:column;gap:1rem;">
                <div style="font-size:3rem;opacity:0.3;">🧬</div>
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                             letter-spacing:3px;color:var(--text-dim);">
                    AWAITING INPUT
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LAB ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
elif "Lab" in page:
    st.markdown("""
    <div class="hg-hero" style="text-align:left;padding:1rem 0;">
        <div class="hg-section-title">🔬 Lab Report Analyzer</div>
        <div style="font-size:0.8rem;color:var(--text-dim);letter-spacing:1px;margin-top:0.3rem;">
            Enter lab test values for instant interpretation
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    LAB_REFERENCE = {
        "Hemoglobin": {"unit": "g/dL", "male": (13.5, 17.5), "female": (12.0, 15.5), "general": (12.0, 17.5), "critical_low": 7.0, "critical_high": 20.0},
        "Glucose (Fasting)": {"unit": "mg/dL", "general": (70, 100), "critical_low": 40, "critical_high": 500},
        "Creatinine": {"unit": "mg/dL", "male": (0.7, 1.3), "female": (0.5, 1.1), "general": (0.5, 1.3)},
        "WBC": {"unit": "10³/µL", "general": (4.5, 11.0), "critical_low": 2.0, "critical_high": 30.0},
        "Platelets": {"unit": "10³/µL", "general": (150, 400), "critical_low": 50, "critical_high": 1000},
        "Sodium": {"unit": "mEq/L", "general": (136, 145), "critical_low": 120, "critical_high": 160},
        "Potassium": {"unit": "mEq/L", "general": (3.5, 5.0), "critical_low": 2.5, "critical_high": 6.5},
        "TSH": {"unit": "mIU/L", "general": (0.4, 4.0)},
        "HbA1c": {"unit": "%", "general": (0, 5.7)},
        "ALT": {"unit": "U/L", "general": (7, 56)},
        "Total Cholesterol": {"unit": "mg/dL", "general": (0, 200)},
    }

    def interpret_value(test, value, sex=None):
        ref = LAB_REFERENCE.get(test)
        if not ref:
            return "UNKNOWN", "grey", "No reference data available."

        if sex and sex in ["male", "female"] and sex in ref:
            lo, hi = ref[sex]
        else:
            lo, hi = ref.get("general", (None, None))

        crit_lo = ref.get("critical_low", float('-inf'))
        crit_hi = ref.get("critical_high", float('inf'))

        if lo is None:
            return "UNKNOWN", "grey", "Cannot determine range."

        if value <= crit_lo:
            return "CRITICAL LOW", "#ff003c", f"Dangerously low! Normal: {lo}–{hi} {ref['unit']}"
        elif value >= crit_hi:
            return "CRITICAL HIGH", "#ff003c", f"Dangerously high! Normal: {lo}–{hi} {ref['unit']}"
        elif value < lo:
            return "LOW", "#ffcc00", f"Below normal range ({lo}–{hi} {ref['unit']})"
        elif value > hi:
            return "HIGH", "#ff6432", f"Above normal range ({lo}–{hi} {ref['unit']})"
        else:
            return "NORMAL", "#00ff88", f"Within normal range ({lo}–{hi} {ref['unit']})"

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown('<div class="hg-label">Test Name</div>', unsafe_allow_html=True)
        test_name = st.selectbox("", list(LAB_REFERENCE.keys()), label_visibility="collapsed")

        st.markdown('<div class="hg-label" style="margin-top:0.8rem;">Value</div>', unsafe_allow_html=True)
        unit = LAB_REFERENCE[test_name]["unit"]
        value = st.number_input(f"({unit})", min_value=0.0, max_value=10000.0,
                                value=0.0, step=0.1, format="%.2f")

        st.markdown('<div class="hg-label" style="margin-top:0.8rem;">Patient Sex</div>', unsafe_allow_html=True)
        sex_opt = st.radio("", ["Not specified", "Male", "Female"],
                           horizontal=True, label_visibility="collapsed")

        interpret_btn = st.button("🔬  INTERPRET VALUE", use_container_width=True)

    with col_out:
        if interpret_btn and value > 0:
            sex_map = {"Male": "male", "Female": "female", "Not specified": None}
            status, color, msg = interpret_value(test_name, value, sex_map[sex_opt])

            badge_class = {
                "NORMAL": "badge-normal",
                "LOW": "badge-low",
                "HIGH": "badge-high",
                "CRITICAL LOW": "badge-critical",
                "CRITICAL HIGH": "badge-critical",
            }.get(status, "badge-normal")

            st.markdown(f"""
            <div class="hg-card">
                <div style="margin-bottom:1rem;">
                    <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                                letter-spacing:2px;color:var(--text-dim);">TEST RESULT</div>
                    <div style="font-family:'Orbitron',monospace;font-size:1.5rem;
                                color:{color};margin:0.5rem 0;font-weight:700;">
                        {value:.2f} <span style="font-size:0.9rem;opacity:0.7;">{unit}</span>
                    </div>
                    <span class="status-badge {badge_class}">{status}</span>
                </div>
                <div class="hg-divider"></div>
                <div style="margin-top:1rem;">
                    <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                                letter-spacing:2px;color:var(--text-dim);margin-bottom:0.5rem;">
                        INTERPRETATION
                    </div>
                    <div style="font-size:0.85rem;color:var(--text-main);line-height:1.6;">
                        {msg}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if "CRITICAL" in status:
                st.markdown("""
                <div class="disclaimer-box" style="border-color:rgba(255,0,60,0.4);
                                                    background:rgba(255,0,60,0.08);
                                                    color:#ff6469;">
                    🚨 CRITICAL VALUE DETECTED — Seek immediate medical attention.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:220px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed rgba(0,212,255,0.15);border-radius:12px;
                        flex-direction:column;gap:1rem;">
                <div style="font-size:3rem;opacity:0.3;">🔬</div>
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                             letter-spacing:3px;color:var(--text-dim);">
                    ENTER A VALUE TO INTERPRET
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MEDICAL Q&A
# ══════════════════════════════════════════════════════════════════════════════
elif "Q&A" in page:
    st.markdown("""
    <div class="hg-hero" style="text-align:left;padding:1rem 0;">
        <div class="hg-section-title">💬 Medical Q&A Engine</div>
        <div style="font-size:0.8rem;color:var(--text-dim);letter-spacing:1px;margin-top:0.3rem;">
            Ask any medical question — powered by RAG over 47K+ medical QA pairs
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    # Sample questions
    st.markdown('<div class="hg-label">Quick Questions</div>', unsafe_allow_html=True)
    sample_qs = [
        "What is Type 2 Diabetes?",
        "What causes high blood pressure?",
        "What are the symptoms of anemia?",
        "How is hypothyroidism treated?",
    ]
    cols = st.columns(4)
    selected_sample = None
    for col, q in zip(cols, sample_qs):
        with col:
            if st.button(q, use_container_width=True):
                selected_sample = q

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="hg-label">Your Question</div>', unsafe_allow_html=True)

    question = st.text_input(
        "",
        value=selected_sample or "",
        placeholder="e.g. What are the early signs of kidney disease?",
        label_visibility="collapsed"
    )

    ask_btn = st.button("💬  GET ANSWER", use_container_width=False)

    if ask_btn or selected_sample:
        q = question.strip() or (selected_sample or "").strip()
        if q:
            with st.spinner(""):
                st.markdown("""
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                            letter-spacing:3px;color:var(--electric-blue);
                            animation:pulse-glow 1s infinite;">
                    ⚡ QUERYING KNOWLEDGE BASE...
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1.2)

            data, err = api_call("/qa", {"text": q})

            st.markdown(f"""
            <div class="result-card-green" style="margin-top:1rem;">
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                            letter-spacing:2px;color:var(--text-dim);margin-bottom:0.5rem;">
                    QUESTION
                </div>
                <div style="font-size:0.9rem;color:var(--electric-blue);">{q}</div>
            </div>
            """, unsafe_allow_html=True)

            if err == "backend_offline":
                st.markdown("""
                <div class="hg-card" style="margin-top:0.5rem;">
                    <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                                letter-spacing:2px;color:var(--text-dim);margin-bottom:0.8rem;">
                        ANSWER <span style="color:#ffcc00;">[DEMO MODE]</span>
                    </div>
                    <div style="font-size:0.9rem;line-height:1.8;color:var(--text-main);">
                        The QA Engine will answer this when the backend model is connected.
                        It uses RAG (Retrieval-Augmented Generation) over your cleaned
                        MedQuAD + MedQA datasets — finding the most relevant medical
                        knowledge and generating a clear explanation.
                    </div>
                    <div style="margin-top:1rem;font-family:'Orbitron',monospace;
                                font-size:0.6rem;letter-spacing:2px;color:var(--text-dim);">
                        SOURCES: MedQuAD · MedQA-USMLE · MedMCQA
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif data:
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                st.markdown(f"""
                <div class="hg-card" style="margin-top:0.5rem;">
                    <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                                letter-spacing:2px;color:var(--text-dim);margin-bottom:0.8rem;">
                        ANSWER
                    </div>
                    <div style="font-size:0.9rem;line-height:1.8;">{answer}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="disclaimer-box" style="margin-top:1rem;">
                This answer is generated from a medical knowledge base.
                Always verify with a healthcare professional.
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OCR SCANNER
# ══════════════════════════════════════════════════════════════════════════════
elif "OCR" in page:
    st.markdown("""
    <div class="hg-hero" style="text-align:left;padding:1rem 0;">
        <div class="hg-section-title">📄 OCR Report Scanner</div>
        <div style="font-size:0.8rem;color:var(--text-dim);letter-spacing:1px;margin-top:0.3rem;">
            Upload a medical report image — extract and analyze its text
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="hg-divider"></div>', unsafe_allow_html=True)

    col_up, col_out = st.columns([1, 1], gap="large")

    with col_up:
        st.markdown('<div class="hg-label">Upload Report</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "",
            type=["png", "jpg", "jpeg", "pdf"],
            label_visibility="collapsed"
        )

        st.markdown("""
        <div style="font-size:0.7rem;color:var(--text-dim);margin-top:0.5rem;
                    letter-spacing:1px;">
            Supported: PNG, JPG, JPEG, PDF · Max 10MB
        </div>
        """, unsafe_allow_html=True)

        if uploaded:
            st.markdown('<br>', unsafe_allow_html=True)
            if uploaded.type.startswith("image"):
                st.image(uploaded, caption="Uploaded Report", use_column_width=True)
            else:
                st.markdown("""
                <div class="result-card">
                    <div style="font-family:'Orbitron',monospace;font-size:0.75rem;
                                color:var(--electric-blue);">📄 PDF Uploaded</div>
                    <div style="font-size:0.8rem;color:var(--text-dim);margin-top:0.3rem;">
                        PDF processing will extract text from all pages.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            scan_btn = st.button("📄  EXTRACT & ANALYZE", use_container_width=True)
        else:
            scan_btn = False
            st.markdown("""
            <div style="height:180px;display:flex;align-items:center;justify-content:center;
                        border:2px dashed rgba(0,212,255,0.15);border-radius:12px;
                        flex-direction:column;gap:1rem;margin-top:1rem;">
                <div style="font-size:3rem;opacity:0.3;">📤</div>
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                             letter-spacing:3px;color:var(--text-dim);">
                    DRAG & DROP OR CLICK TO UPLOAD
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_out:
        if scan_btn:
            with st.spinner("Scanning..."):
                time.sleep(2)
            st.markdown("""
            <div class="hg-card">
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                            letter-spacing:2px;color:var(--text-dim);margin-bottom:0.8rem;">
                    EXTRACTED TEXT <span style="color:#ffcc00;">[OCR MODULE PENDING]</span>
                </div>
                <div style="font-size:0.85rem;color:var(--text-main);line-height:1.8;
                            font-family:monospace;background:rgba(0,10,30,0.5);
                            border-radius:8px;padding:1rem;">
                    Patient: [Name]<br>
                    Date: [Date]<br>
                    Test: Complete Blood Count<br>
                    ─────────────────────<br>
                    Hemoglobin: 11.2 g/dL ↓<br>
                    WBC: 8.5 × 10³/µL<br>
                    Platelets: 220 × 10³/µL<br>
                    ─────────────────────<br>
                    <span style="color:#ffcc00;">[OCR module connects when backend is ready]</span>
                </div>
                <div style="margin-top:1rem;font-family:'Orbitron',monospace;
                            font-size:0.6rem;letter-spacing:2px;color:var(--text-dim);">
                    ENGINE: Tesseract + EasyOCR
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif not uploaded:
            st.markdown("""
            <div style="height:300px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed rgba(0,212,255,0.15);border-radius:12px;
                        flex-direction:column;gap:1rem;">
                <div style="font-size:3rem;opacity:0.3;">🔍</div>
                <div style="font-family:'Orbitron',monospace;font-size:0.65rem;
                             letter-spacing:3px;color:var(--text-dim);">
                    UPLOAD A REPORT TO BEGIN
                </div>
            </div>
            """, unsafe_allow_html=True)