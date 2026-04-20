import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="HealthGuard AI",
    page_icon="🏥",
    layout="wide"
)

# ── GLOBAL CSS ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Orbitron:wght@400;700;900&display=swap');

html, body, [data-testid="stApp"] {
    background: radial-gradient(ellipse at top, #020617 0%, #000000 100%);
    color: #E2E8F0;
    font-family: 'Space Grotesk', sans-serif;
}

/* Animated background particles */
[data-testid="stApp"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(circle at 20% 50%, rgba(0,198,255,0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(0,114,255,0.03) 0%, transparent 50%),
        radial-gradient(circle at 50% 80%, rgba(120,0,255,0.03) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: rgba(2, 6, 23, 0.95) !important;
    border-right: 1px solid rgba(0,198,255,0.15) !important;
    backdrop-filter: blur(20px);
}

[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00c6ff, #0072ff, transparent);
}

/* Nav buttons in sidebar */
div.stButton > button {
    width: 100%;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #E2E8F0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    text-align: left !important;
    padding: 12px 16px !important;
}

div.stButton > button:hover {
    background: rgba(0,198,255,0.1) !important;
    border-color: rgba(0,198,255,0.4) !important;
    transform: translateX(4px) !important;
    box-shadow: 0 0 20px rgba(0,198,255,0.15) !important;
    color: #00c6ff !important;
}

/* Primary action buttons */
div.stButton > button[kind="primary"],
.action-btn > div.stButton > button {
    background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(0,114,255,0.3) !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,114,255,0.5) !important;
}

/* Module cards on home page */
.module-card {
    position: relative;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 28px 24px;
    cursor: pointer;
    transition: all 0.4s ease;
    overflow: hidden;
    text-decoration: none;
}

.module-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(0,198,255,0.05), rgba(0,114,255,0.05));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.module-card:hover {
    border-color: rgba(0,198,255,0.4);
    transform: translateY(-8px);
    box-shadow: 0 20px 60px rgba(0,198,255,0.15), 0 0 0 1px rgba(0,198,255,0.2);
}

.module-card:hover::before { opacity: 1; }

.module-card .icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
    display: block;
}

.module-card h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #F8FAFC;
}

.module-card p {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
    margin: 0;
}

.module-card .glow-dot {
    position: absolute;
    top: 16px; right: 16px;
    width: 8px; height: 8px;
    background: #00c6ff;
    border-radius: 50%;
    box-shadow: 0 0 10px #00c6ff;
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
}

/* Stats bar */
.stat-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
}

.stat-box:hover {
    border-color: rgba(0,198,255,0.3);
    box-shadow: 0 0 30px rgba(0,198,255,0.08);
}

.stat-box .num {
    font-family: 'Orbitron', monospace;
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-box .label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.4);
    margin-top: 4px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Result cards */
.result-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 24px;
    margin-top: 16px;
    position: relative;
    overflow: hidden;
}

.result-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
}

/* Chat bubbles */
.chat-user {
    background: rgba(0,198,255,0.08);
    border: 1px solid rgba(0,198,255,0.15);
    padding: 14px 18px;
    border-radius: 16px 16px 4px 16px;
    margin-bottom: 12px;
    animation: fadeSlideIn 0.3s ease;
}

.chat-ai {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 14px 18px;
    border-radius: 16px 16px 16px 4px;
    margin-bottom: 12px;
    animation: fadeSlideIn 0.3s ease;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

.chat-user b { color: #00c6ff; }
.chat-ai  b  { color: #7c3aed; }

.module-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(0,198,255,0.1);
    border: 1px solid rgba(0,198,255,0.2);
    color: #00c6ff;
    font-size: 11px;
    margin-top: 8px;
    letter-spacing: 0.03em;
}

/* Inputs */
textarea, [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

textarea:focus, [data-testid="stTextInput"] input:focus {
    border-color: rgba(0,198,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,198,255,0.1) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
}

/* Section headers */
.section-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
}

.section-sub {
    color: rgba(255,255,255,0.45);
    font-size: 0.9rem;
    margin-bottom: 24px;
}

/* Back button special style */
.back-btn div.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    width: auto !important;
    padding: 8px 16px !important;
    font-size: 0.85rem !important;
}

/* Divider glow */
hr {
    border-color: rgba(255,255,255,0.06) !important;
}

/* Status indicator */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.2);
    color: #22c55e;
    font-size: 12px;
    font-weight: 500;
}

/* Number input */
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0,198,255,0.2);
    border-radius: 3px;
}

/* Warning/info boxes */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)


# ── SESSION STATE ─────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm HealthGuard AI 👋 Describe symptoms, paste lab values, or ask any medical question.",
        "module": None, "confidence": None, "raw_result": None
    }]
if "qa_chat" not in st.session_state:
    st.session_state.qa_chat = []


# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 16px 0;">
        <div style="font-family:'Orbitron',monospace; font-size:1.1rem; font-weight:700;
                    background:linear-gradient(135deg,#00c6ff,#0072ff);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            HealthGuard AI
        </div>
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.35); margin-top:2px;">
            AI-powered medical assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("<div style='font-size:0.7rem; color:rgba(255,255,255,0.3); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px;'>Navigation</div>", unsafe_allow_html=True)

    pages = [
        ("🏠", "Home",              "home"),
        ("🤖", "AI Chat Assistant", "chat"),
        ("🩺", "Disease Predictor", "disease"),
        ("🧪", "Lab Analyzer",      "lab"),
        ("❓", "Medical Q&A",       "qa"),
        ("📄", "Upload Report",     "ocr"),
    ]

    for icon, label, key in pages:
        active = "→ " if st.session_state.page == key else ""
        if st.button(f"{icon}  {active}{label}", key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()

    st.divider()

    # API Status
    st.markdown("<div style='font-size:0.7rem; color:rgba(255,255,255,0.3); letter-spacing:0.1em; text-transform:uppercase; margin-bottom:8px;'>API Status</div>", unsafe_allow_html=True)
    try:
        res = requests.get(f"{API_URL}/health", timeout=3)
        if res.status_code == 200:
            modules = res.json().get("modules", {})
            if modules:
                for name, status in modules.items():
                    icon  = "🟢" if status in ["ready","running","ok"] else "🔴"
                    label_text = name.replace("_"," ").title()
                    st.markdown(f"<div style='font-size:0.8rem; padding:4px 0; color:rgba(255,255,255,0.6);'>{icon} {label_text}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='status-pill'>🟢 Connected</div>", unsafe_allow_html=True)
    except:
        st.markdown("<div style='font-size:0.8rem; color:#ef4444;'>❌ API Offline</div>", unsafe_allow_html=True)
        st.caption("Run: `uvicorn api.main:app --reload`")

    st.divider()

    if st.button("🔄  Clear Chat History"):
        st.session_state.messages  = [{
            "role": "assistant",
            "content": "Hello! I'm HealthGuard AI 👋 How can I help?",
            "module": None, "confidence": None, "raw_result": None
        }]
        st.session_state.qa_chat = []
        try: requests.post(f"{API_URL}/reset", timeout=3)
        except: pass
        st.rerun()

    st.divider()
    st.caption("⚠️ Not a substitute for professional medical advice.")


# ══════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════
def show_home():
    time_now = datetime.datetime.now().strftime("%H:%M")

    # ── SPLINE HERO
    components.html(f"""
    <div style="position:relative; width:100%; height:520px; border-radius:24px; overflow:hidden; margin-bottom:32px;">

        <iframe
            src="https://my.spline.design/visualicons-rAtMGxPoVJ5jOAnvcHyOiEPW/"
            frameborder="0"
            style="width:100%; height:100%; border:none; pointer-events:none;">
        </iframe>

        <!-- gradient overlay -->
        <div style="
            position:absolute; inset:0;
            background: linear-gradient(to right,
                rgba(2,6,23,0.97) 0%,
                rgba(2,6,23,0.75) 40%,
                rgba(2,6,23,0.2)  70%,
                transparent 100%);
        "></div>

        <!-- text content -->
        <div style="
            position:absolute; top:50%; left:64px;
            transform:translateY(-50%); color:white; z-index:2;
        ">
            <div style="
                font-family:'Orbitron',monospace;
                font-size:0.7rem; letter-spacing:0.2em;
                color:#00c6ff; text-transform:uppercase;
                margin-bottom:12px;
            ">AI · Medical · Assistant</div>

            <h1 style="
                font-family:'Orbitron',monospace;
                font-size:3.2rem; font-weight:900;
                margin:0 0 8px 0; line-height:1.1;
                background:linear-gradient(135deg,#ffffff 0%,rgba(255,255,255,0.7) 100%);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            ">HealthGuard<br>AI</h1>

            <p style="opacity:0.6; font-size:1rem; margin:0 0 24px 0;">
                Intelligent diagnostics powered by machine learning
            </p>

            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <div style="
                    padding:8px 16px;
                    background:rgba(0,198,255,0.1);
                    border:1px solid rgba(0,198,255,0.25);
                    border-radius:20px;
                    font-size:0.8rem; color:#00c6ff;
                ">🟢 System Active</div>
                <div style="
                    padding:8px 16px;
                    background:rgba(255,255,255,0.06);
                    border:1px solid rgba(255,255,255,0.1);
                    border-radius:20px;
                    font-size:0.8rem;
                ">🕐 {time_now}</div>
                <div style="
                    padding:8px 16px;
                    background:rgba(255,255,255,0.06);
                    border:1px solid rgba(255,255,255,0.1);
                    border-radius:20px;
                    font-size:0.8rem;
                ">⚡ 4 Modules Ready</div>
            </div>
        </div>

        <!-- floating vitals cards -->
        <div style="
            position:absolute; top:50%; right:64px;
            transform:translateY(-50%);
            display:flex; flex-direction:column; gap:10px;
            z-index:2;
        ">
            <div style="
                padding:14px 20px;
                background:rgba(2,6,23,0.7);
                backdrop-filter:blur(20px);
                border:1px solid rgba(255,255,255,0.08);
                border-radius:14px;
                display:flex; align-items:center; gap:10px;
            ">
                <span style="font-size:1.3rem;">❤️</span>
                <div>
                    <div style="font-size:0.7rem; color:rgba(255,255,255,0.4);">HEART RATE</div>
                    <div style="font-weight:600;">98 bpm</div>
                </div>
            </div>
            <div style="
                padding:14px 20px;
                background:rgba(2,6,23,0.7);
                backdrop-filter:blur(20px);
                border:1px solid rgba(255,255,255,0.08);
                border-radius:14px;
                display:flex; align-items:center; gap:10px;
            ">
                <span style="font-size:1.3rem;">🩸</span>
                <div>
                    <div style="font-size:0.7rem; color:rgba(255,255,255,0.4);">BLOOD PRESSURE</div>
                    <div style="font-weight:600;">116/70</div>
                </div>
            </div>
            <div style="
                padding:14px 20px;
                background:rgba(2,6,23,0.7);
                backdrop-filter:blur(20px);
                border:1px solid rgba(255,255,255,0.08);
                border-radius:14px;
                display:flex; align-items:center; gap:10px;
            ">
                <span style="font-size:1.3rem;">🧪</span>
                <div>
                    <div style="font-size:0.7rem; color:rgba(255,255,255,0.4);">STATUS</div>
                    <div style="font-weight:600; color:#22c55e;">Stable</div>
                </div>
            </div>
        </div>

    </div>
    """, height=560)

    # ── STATS BAR
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("41",   "Diseases Tracked"),
        ("41K+", "QA Pairs"),
        ("18+",  "Lab Tests"),
        ("0",    "External APIs"),
    ]
    for col, (num, label) in zip([c1,c2,c3,c4], stats):
        col.markdown(f"""
        <div class="stat-box">
            <div class="num">{num}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MODULE CARDS
    st.markdown("""
    <div class="section-title">Choose a Module</div>
    <div class="section-sub">Select any module to get started</div>
    """, unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)

    modules_info = [
        (mc1, "🤖", "AI Chat",        "chat",    "Natural language interface — describe anything"),
        (mc2, "🩺", "Disease Predictor","disease", "Analyze symptoms & predict conditions"),
        (mc3, "🧪", "Lab Analyzer",   "lab",     "Interpret your lab report values"),
        (mc4, "📄", "Report Scanner", "ocr",     "Upload & extract text from reports"),
    ]

    for col, icon, title, key, desc in modules_info:
        with col:
            st.markdown(f"""
            <div class="module-card" onclick="">
                <div class="glow-dot"></div>
                <span class="icon">{icon}</span>
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title} →", key=f"home_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HOW IT WORKS
    st.markdown("""
    <div class="section-title">How it Works</div>
    <div class="section-sub">Three simple steps to get your health insights</div>
    """, unsafe_allow_html=True)

    h1, h2, h3 = st.columns(3)
    steps = [
        ("01", "Input", "Describe symptoms, enter lab values, or upload a report"),
        ("02", "Analyze", "Our AI models process your data across multiple modules"),
        ("03", "Understand", "Get clear explanations with confidence scores"),
    ]
    for col, (num, title, desc) in zip([h1,h2,h3], steps):
        col.markdown(f"""
        <div class="result-card" style="text-align:center;">
            <div style="font-family:'Orbitron',monospace; font-size:2rem; font-weight:900;
                        background:linear-gradient(135deg,#00c6ff,#0072ff);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                {num}
            </div>
            <h3 style="margin:8px 0 6px; font-size:1rem;">{title}</h3>
            <p style="color:rgba(255,255,255,0.45); font-size:0.85rem; margin:0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# AI CHAT ASSISTANT
# ══════════════════════════════════════════════════
def show_chat():
    st.markdown('<div class="section-title">🤖 AI Chat Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Describe symptoms, ask questions, or paste lab values</div>', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        css   = "chat-user" if msg["role"] == "user" else "chat-ai"
        label = "You" if msg["role"] == "user" else "HealthGuard AI"
        badge = ""
        if msg.get("module"):
            conf  = round(msg["confidence"] * 100, 1) if msg.get("confidence") else 0
            badge = f"<br><span class='module-badge'>🔧 {msg['module']} &nbsp;|&nbsp; 📊 {conf}%</span>"
        st.markdown(f"""
        <div class="{css}">
            <b>{label}</b><br>{msg["content"]}{badge}
        </div>
        """, unsafe_allow_html=True)

        if msg.get("raw_result"):
            with st.expander("🔍 Detailed analysis"):
                st.json(msg["raw_result"])

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("msg", placeholder="Describe symptoms, paste lab values, or ask a medical question...",
                                   label_visibility="collapsed", key="chat_input")
    with col2:
        send = st.button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        st.session_state.messages.append({
            "role": "user", "content": user_input,
            "module": None, "confidence": None, "raw_result": None
        })
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={"message": user_input}, timeout=120)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.messages.append({
                        "role":       "assistant",
                        "content":    data.get("response", "Sorry, something went wrong."),
                        "module":     data.get("module_used"),
                        "confidence": data.get("confidence", 0.0),
                        "raw_result": data.get("raw_result", {})
                    })
                    if data.get("disclaimer"):
                        st.warning(f"⚠️ {data['disclaimer']}")
                else:
                    st.error(f"API error: {res.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timed out. Try again.")
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()


# ══════════════════════════════════════════════════
# DISEASE PREDICTOR
# ══════════════════════════════════════════════════
def show_disease():
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()

    st.markdown('<div class="section-title">🩺 Disease Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Describe your symptoms for an AI-powered diagnosis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 0.7])

    with col1:
        symptoms = st.text_area("Symptoms", placeholder="e.g. fever, headache, body ache, fatigue for 3 days...", height=140)
        age = st.number_input("Age", min_value=0, max_value=120, value=0)
        sex = st.selectbox("Sex (optional)", ["", "male", "female"])
        if st.button("🔍 Analyze Symptoms", use_container_width=True):
            if symptoms:
                with st.spinner("Analyzing..."):
                    try:
                        res  = requests.post(f"{API_URL}/predict/disease", json={
                            "text": symptoms,
                            "age":  age if age > 0 else None,
                            "sex":  sex if sex else None
                        }, timeout=60)
                        data = res.json()
                        expl = data.get("explanation") or data.get("result", "Analysis complete.")
                        st.markdown(f'<div class="result-card"><h3>🔬 Analysis</h3><p>{expl}</p></div>', unsafe_allow_html=True)
                        diseases = data.get("raw_result", {}).get("diseases") or data.get("predictions", [])
                        if diseases:
                            st.subheader("Top Predictions")
                            cols = st.columns(min(len(diseases), 3))
                            for i, d in enumerate(diseases[:3]):
                                name = d.get("name") or d.get("disease", "Unknown")
                                conf = d.get("confidence", 0)
                                with cols[i]:
                                    st.metric(str(name).title(), f"{round(conf*100)}%")
                        with st.expander("🔍 Full response"): st.json(data)
                        st.warning("⚠️ Not a substitute for professional medical advice.")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please describe your symptoms.")

    with col2:
        st.markdown("""
        <div class="result-card">
            <h4 style="margin-top:0;">💡 Tips</h4>
            <ul style="color:rgba(255,255,255,0.6); font-size:0.85rem; padding-left:16px;">
                <li>Be specific about symptoms</li>
                <li>Include duration</li>
                <li>Mention severity</li>
                <li>Add relevant history</li>
            </ul>
            <h4>⚠️ Common Symptoms</h4>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
        """, unsafe_allow_html=True)
        for s in ["Fever","Headache","Fatigue","Nausea","Chest pain","Cough","Dizziness"]:
            st.markdown(f"<span class='module-badge'>{s}</span>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# LAB ANALYZER
# ══════════════════════════════════════════════════
def show_lab():
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()

    st.markdown('<div class="section-title">🧪 Lab Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Enter your lab values for instant interpretation</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        test = st.selectbox("Test Name", [
            "hemoglobin","glucose_fasting","hba1c","creatinine","wbc","platelets",
            "tsh","sodium","potassium","total_cholesterol","ldl","hdl",
            "alt","ast","total_bilirubin","bun","calcium","triglycerides"
        ])
        value = st.number_input("Value", min_value=0.0, step=0.1, format="%.2f")
        sex   = st.selectbox("Sex (optional)", ["","male","female"])

        if st.button("🔬 Interpret Result", use_container_width=True):
            with st.spinner("Interpreting..."):
                try:
                    res    = requests.post(f"{API_URL}/analyze/lab", json={
                        "test_name": test, "value": value,
                        "sex": sex if sex else None
                    }, timeout=30)
                    data   = res.json()
                    status = data.get("result",{}).get("status","") or data.get("status","")
                    color  = "#ef4444" if "HIGH" in str(status).upper() else "#f59e0b" if "LOW" in str(status).upper() else "#22c55e"
                    normal = data.get("result",{}).get("normal_range") or data.get("normal_range","N/A")
                    unit   = data.get("result",{}).get("unit") or data.get("unit","")
                    expl   = data.get("explanation") or data.get("interpretation","")
                    st.markdown(f"""
                    <div class="result-card" style="border-left:4px solid {color};">
                        <h3 style="color:{color}; margin-top:0;">{status or 'Result'}</h3>
                        <p>{expl}</p>
                        <p style="color:rgba(255,255,255,0.5); font-size:0.85rem;">
                            <b>Normal Range:</b> {normal} {unit}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("🔍 Full response"): st.json(data)
                    st.warning("⚠️ Not a substitute for professional medical advice.")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.markdown("""
        <div class="result-card">
            <h4 style="margin-top:0;">📋 Common Normal Ranges</h4>
            <table style="width:100%; font-size:0.82rem; border-collapse:collapse;">
        """, unsafe_allow_html=True)
        ranges = [
            ("Hemoglobin",   "M: 13.5–17.5 g/dL"),
            ("Glucose",      "70–100 mg/dL"),
            ("HbA1c",        "< 5.7%"),
            ("Cholesterol",  "< 200 mg/dL"),
            ("TSH",          "0.4–4.0 mIU/L"),
            ("Creatinine",   "0.6–1.3 mg/dL"),
            ("WBC",          "4.5–11.0 K/µL"),
            ("Platelets",    "150–400 K/µL"),
        ]
        for name, val in ranges:
            st.markdown(f"""
            <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                <td style="padding:6px 0; color:rgba(255,255,255,0.6);">{name}</td>
                <td style="padding:6px 0; color:#00c6ff; text-align:right;">{val}</td>
            </tr>
            """, unsafe_allow_html=True)
        st.markdown("</table></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════
# MEDICAL Q&A
# ══════════════════════════════════════════════════
def show_qa():
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()

    st.markdown('<div class="section-title">❓ Medical Q&A</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ask any medical question</div>', unsafe_allow_html=True)

    for msg in st.session_state.qa_chat:
        css   = "chat-user" if msg["role"] == "You" else "chat-ai"
        st.markdown(f'<div class="{css}"><b>{msg["role"]}</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

    q    = st.text_input("Question", placeholder="e.g. What causes high blood pressure?")
    send = st.button("Ask ➤")

    if send and q.strip():
        st.session_state.qa_chat.append({"role": "You", "content": q})
        with st.spinner("Searching knowledge base..."):
            try:
                res = requests.post(f"{API_URL}/qa", json={"question": q}, timeout=60)
                ans = res.json().get("explanation") or res.json().get("answer","No answer found.")
                st.session_state.qa_chat.append({"role": "AI", "content": ans})
            except requests.exceptions.ConnectionError:
                st.session_state.qa_chat.append({"role": "AI", "content": "❌ Cannot connect to API."})
            except Exception as e:
                st.session_state.qa_chat.append({"role": "AI", "content": f"Error: {e}"})
        st.rerun()

    st.caption("⚠️ Not a substitute for professional medical advice.")


# ══════════════════════════════════════════════════
# UPLOAD REPORT (OCR)
# ══════════════════════════════════════════════════
def show_ocr():
    if st.button("← Back to Home"):
        st.session_state.page = "home"; st.rerun()

    st.markdown('<div class="section-title">📄 Upload Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Upload a lab report image or PDF for text extraction</div>', unsafe_allow_html=True)

    file = st.file_uploader("Upload file", type=["png","jpg","jpeg","pdf"], help="PNG, JPG, JPEG, PDF supported")

    if file:
        if file.type.startswith("image"):
            st.image(file, caption="Uploaded Report", use_column_width=True)
        else:
            st.info(f"📄 `{file.name}`")

        if st.button("🔍 Extract & Analyze"):
            with st.spinner("Extracting text..."):
                try:
                    res  = requests.post(f"{API_URL}/ocr",
                                         files={"file": (file.name, file.getvalue(), file.type)}, timeout=60)
                    data = res.json()
                    text = (data.get("result",{}).get("extracted_text")
                            or data.get("text","")
                            or data.get("extracted_text",""))
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>📝 Extracted Text</h3>
                        <pre style="white-space:pre-wrap; font-size:0.85rem; color:rgba(255,255,255,0.75);">{text if text else "⏳ OCR module coming soon."}</pre>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("🔍 Full response"): st.json(data)
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API.")
                except Exception as e:
                    st.error(f"Error: {e}")


# ══════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════
page = st.session_state.page

if   page == "home":    show_home()
elif page == "chat":    show_chat()
elif page == "disease": show_disease()
elif page == "lab":     show_lab()
elif page == "qa":      show_qa()
elif page == "ocr":     show_ocr()