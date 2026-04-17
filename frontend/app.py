import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="HealthGuard AI", layout="wide")

# ── THEME ─────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme_toggle = st.toggle("🌗 Light Mode", value=False)
st.session_state.theme = "light" if theme_toggle else "dark"

bg = "#020617" if st.session_state.theme == "dark" else "#F8FAFC"
text = "#F8FAFC" if st.session_state.theme == "dark" else "#1E293B"

# ── GLOBAL CSS ─────────────────
st.markdown(f"""
<style>
html, body, [data-testid="stApp"] {{
    background: {bg};
    color: {text};
    font-family: 'Segoe UI';
}}

textarea, input, select {{
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
}}

button {{
    border-radius: 12px !important;
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: white !important;
}}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────
time_now = datetime.datetime.now().strftime("%H:%M")

components.html(f"""
<div style="position:relative; width:100%; height:520px; border-radius:30px; overflow:hidden;">

    <!-- ✅ FIXED IFRAME -->
    <iframe 
        src="https://my.spline.design/visualicons-rAtMGxPoVJ5jOAnvcHyOiEPW/"
        frameborder="0"
        style="width:100%; height:100%; border:none;">
    </iframe>

    <!-- overlay -->
    <div style="
        position:absolute;
        inset:0;
        background: linear-gradient(
            to right,
            rgba(2,6,23,0.95),
            rgba(2,6,23,0.6),
            rgba(2,6,23,0.2),
            transparent
        );
    "></div>

    <!-- text -->
    <div style="
        position:absolute;
        top:50%;
        left:60px;
        transform:translateY(-50%);
        color:white;
    ">
        <h1 style="font-size:3rem;">HealthGuard AI</h1>
        <p style="opacity:0.8;">AI-powered medical assistant</p>

        <div style="margin-top:20px; display:flex; gap:10px;">
            <div style="padding:8px 14px; background:rgba(255,255,255,0.1); border-radius:10px;">
                🟢 Active
            </div>
            <div style="padding:8px 14px; background:rgba(255,255,255,0.1); border-radius:10px;">
                {time_now}
            </div>
        </div>
    </div>

    <!-- 💎 FLOATING CARDS -->
    <div style="
        position:absolute;
        top:60px;
        right:60px;
        display:flex;
        flex-direction:column;
        gap:12px;
    ">
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">❤️ 98 bpm</div>
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">🩸 116/70</div>
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">🧪 Stable</div>
    </div>

</div>
""", height=520)

# ── SIDEBAR ───────────────────
page = st.sidebar.selectbox("Module", [
    "Disease Predictor",
    "Lab Analyzer",
    "Medical Q&A",
    "Upload Report"
])

# ── DISEASE ───────────────────
if page == "Disease Predictor":

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        symptoms = st.text_area("Symptoms", placeholder="Describe symptoms...")
        age = st.number_input("Age", 0, 120)
        sex = st.selectbox("Sex", ["", "male", "female"])
        analyze = st.button("Analyze", use_container_width=True)

    with col2:
        st.markdown("### AI Tips")
        st.markdown("""
- Be specific  
- Include duration  
- Mention severity  
        """)

    if analyze and symptoms:
        res = requests.post(f"{API_URL}/predict/disease", json={
            "text": symptoms,
            "age": age if age else None,
            "sex": sex if sex else None
        })
        data = res.json()

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:16px;">
            <h3>Diagnosis</h3>
            <p>{data.get("explanation","")}</p>
        </div>
        """, unsafe_allow_html=True)

# ── LAB ───────────────────────
elif page == "Lab Analyzer":

    test = st.selectbox("Test", ["glucose_fasting","hba1c","cholesterol"])
    value = st.number_input("Value")

    if st.button("Analyze"):
        res = requests.post(f"{API_URL}/analyze/lab", json={
            "test_name": test,
            "value": value
        })
        data = res.json()

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:16px;">
            <h3>{data.get("result",{}).get("status","")}</h3>
            <p>{data.get("explanation","")}</p>
        </div>
        """, unsafe_allow_html=True)

# ── CHAT ──────────────────────
elif page == "Medical Q&A":

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:10px;">
            <b>{msg["role"]}</b><br>{msg["content"]}
        </div>
        """, unsafe_allow_html=True)

    q = st.text_input("Ask")

    if st.button("Send") and q:
        st.session_state.chat.append({"role":"You","content":q})

        res = requests.post(f"{API_URL}/qa", json={"question":q})
        ans = res.json().get("explanation","")

        st.session_state.chat.append({"role":"AI","content":ans})
        st.rerun()

# ── OCR ───────────────────────
elif page == "Upload Report":

    file = st.file_uploader("Upload")

    if file and st.button("Analyze"):
        res = requests.post(f"{API_URL}/ocr", files={
            "file": (file.name, file.getvalue())
        })
        data = res.json()

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:16px;">
            <pre>{data.get("result",{}).get("extracted_text","")}</pre>
        </div>
        """, unsafe_allow_html=True)