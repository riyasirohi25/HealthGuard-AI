<<<<<<< HEAD
=======
# frontend/app.py

>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="HealthGuard AI", layout="wide")

<<<<<<< HEAD
# ── THEME ─────────────────────
=======
# ── THEME ─────────────────────────────────────────
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme_toggle = st.toggle("🌗 Light Mode", value=False)
st.session_state.theme = "light" if theme_toggle else "dark"

<<<<<<< HEAD
bg = "#020617" if st.session_state.theme == "dark" else "#F8FAFC"
text = "#F8FAFC" if st.session_state.theme == "dark" else "#1E293B"

# ── GLOBAL CSS ─────────────────
=======
bg   = "#020617" if st.session_state.theme == "dark" else "#F8FAFC"
text = "#F8FAFC" if st.session_state.theme == "dark" else "#1E293B"

# ── GLOBAL CSS ────────────────────────────────────
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
st.markdown(f"""
<style>
html, body, [data-testid="stApp"] {{
    background: {bg};
    color: {text};
    font-family: 'Segoe UI';
}}
<<<<<<< HEAD

=======
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
textarea, input, select {{
    border-radius: 12px !important;
    background: rgba(255,255,255,0.05) !important;
}}
<<<<<<< HEAD

=======
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
button {{
    border-radius: 12px !important;
    background: linear-gradient(135deg, #00c6ff, #0072ff) !important;
    color: white !important;
}}
<<<<<<< HEAD
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────
=======
.result-card {{
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    margin-top: 16px;
}}
.chat-user {{
    background: rgba(0,198,255,0.1);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border-left: 3px solid #00c6ff;
}}
.chat-ai {{
    background: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border-left: 3px solid #0072ff;
}}
.module-badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    background: rgba(0,198,255,0.15);
    color: #00c6ff;
    font-size: 12px;
    margin-top: 8px;
}}
.status-ok  {{ color: #22c55e; }}
.status-err {{ color: #ef4444; }}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
time_now = datetime.datetime.now().strftime("%H:%M")

components.html(f"""
<div style="position:relative; width:100%; height:520px; border-radius:30px; overflow:hidden;">

<<<<<<< HEAD
    <!-- ✅ FIXED IFRAME -->
    <iframe 
=======
    <iframe
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
        src="https://my.spline.design/visualicons-rAtMGxPoVJ5jOAnvcHyOiEPW/"
        frameborder="0"
        style="width:100%; height:100%; border:none;">
    </iframe>

<<<<<<< HEAD
    <!-- overlay -->
    <div style="
        position:absolute;
        inset:0;
=======
    <div style="
        position:absolute; inset:0;
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
        background: linear-gradient(
            to right,
            rgba(2,6,23,0.95),
            rgba(2,6,23,0.6),
            rgba(2,6,23,0.2),
            transparent
        );
    "></div>

<<<<<<< HEAD
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

=======
    <div style="
        position:absolute; top:50%; left:60px;
        transform:translateY(-50%); color:white;
    ">
        <h1 style="font-size:3rem;">HealthGuard AI</h1>
        <p style="opacity:0.8;">AI-powered medical assistant</p>
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
        <div style="margin-top:20px; display:flex; gap:10px;">
            <div style="padding:8px 14px; background:rgba(255,255,255,0.1); border-radius:10px;">
                🟢 Active
            </div>
            <div style="padding:8px 14px; background:rgba(255,255,255,0.1); border-radius:10px;">
                {time_now}
            </div>
        </div>
    </div>

<<<<<<< HEAD
    <!-- 💎 FLOATING CARDS -->
    <div style="
        position:absolute;
        top:60px;
        right:60px;
        display:flex;
        flex-direction:column;
        gap:12px;
=======
    <div style="
        position:absolute; top:60px; right:60px;
        display:flex; flex-direction:column; gap:12px;
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
    ">
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">❤️ 98 bpm</div>
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">🩸 116/70</div>
        <div style="padding:14px; background:rgba(255,255,255,0.08); border-radius:12px;">🧪 Stable</div>
    </div>
<<<<<<< HEAD

</div>
""", height=520)

# ── SIDEBAR ───────────────────
page = st.sidebar.selectbox("Module", [
=======
</div>
""", height=520)

# ── SIDEBAR ───────────────────────────────────────
page = st.sidebar.selectbox("Module", [
    "AI Chat Assistant",
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
    "Disease Predictor",
    "Lab Analyzer",
    "Medical Q&A",
    "Upload Report"
])

<<<<<<< HEAD
# ── DISEASE ───────────────────
if page == "Disease Predictor":
=======
# Module status in sidebar
st.sidebar.divider()
st.sidebar.markdown("**Module Status:**")
try:
    res = requests.get(f"{API_URL}/health", timeout=3)
    if res.status_code == 200:
        modules = res.json().get("modules", {})
        for name, status in modules.items():
            icon  = "🟢" if status in ["ready", "running"] else "🔴"
            label = name.replace("_", " ").title()
            st.sidebar.markdown(f"{icon} {label}: `{status}`")
except:
    st.sidebar.error("❌ API not connected")

st.sidebar.divider()
st.sidebar.caption("⚠️ Not a substitute for professional medical advice.")

# ── PAGE: AI CHAT ASSISTANT ───────────────────────
if page == "AI Chat Assistant":

    st.markdown("## 🤖 AI Chat Assistant")
    st.markdown("Chat naturally — describe symptoms, ask questions, or paste lab values.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role":       "assistant",
            "content":    "Hello! I'm HealthGuard AI 👋 I can help you analyze symptoms, interpret lab reports, and answer medical questions. How can I help you today?",
            "module":     None,
            "confidence": None,
            "raw_result": None
        })

    # Clear button
    if st.button("🔄 Clear Conversation"):
        st.session_state.messages = []
        try:
            requests.post(f"{API_URL}/reset", timeout=3)
        except:
            pass
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-user">
                <b>You</b><br>{msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-ai">
                <b>HealthGuard AI</b><br>{msg["content"]}
                {"<br><span class='module-badge'>🔧 " + msg["module"] + " | 📊 " + str(round(msg["confidence"]*100, 1)) + "%</span>" if msg.get("module") else ""}
            </div>
            """, unsafe_allow_html=True)

            if msg.get("raw_result"):
                with st.expander("🔍 View detailed analysis"):
                    st.json(msg["raw_result"])

    # Chat input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Describe symptoms, paste lab values, or ask a medical question...",
            label_visibility="collapsed"
        )
    with col2:
        send = st.button("Send ➤", use_container_width=True)

    if send and user_input.strip():
        # Add user message
        st.session_state.messages.append({
            "role":       "user",
            "content":    user_input,
            "module":     None,
            "confidence": None,
            "raw_result": None
        })

        # Call API
        with st.spinner("HealthGuard AI is thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    json={"message": user_input},
                    timeout=120
                )
                if res.status_code == 200:
                    data       = res.json()
                    response   = data.get("response", "Sorry, something went wrong.")
                    module     = data.get("module_used", "General Assistant")
                    confidence = data.get("confidence", 0.0)
                    raw_result = data.get("raw_result", {})
                    disclaimer = data.get("disclaimer", "")

                    st.session_state.messages.append({
                        "role":       "assistant",
                        "content":    response,
                        "module":     module,
                        "confidence": confidence,
                        "raw_result": raw_result
                    })

                    if disclaimer:
                        st.warning(f"⚠️ {disclaimer}")
                else:
                    st.error(f"API error: {res.status_code}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Start backend first.")
            except Exception as e:
                st.error(f"Error: {e}")

        st.rerun()

# ── PAGE: DISEASE PREDICTOR ───────────────────────
elif page == "Disease Predictor":
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        symptoms = st.text_area("Symptoms", placeholder="Describe symptoms...")
<<<<<<< HEAD
        age = st.number_input("Age", 0, 120)
        sex = st.selectbox("Sex", ["", "male", "female"])
        analyze = st.button("Analyze", use_container_width=True)
=======
        age      = st.number_input("Age", 0, 120)
        sex      = st.selectbox("Sex", ["", "male", "female"])
        analyze  = st.button("Analyze", use_container_width=True)
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54

    with col2:
        st.markdown("### AI Tips")
        st.markdown("""
<<<<<<< HEAD
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
=======
- Be specific
- Include duration
- Mention severity
        """)

    if analyze and symptoms:
        with st.spinner("Analyzing symptoms..."):
            try:
                res  = requests.post(f"{API_URL}/predict/disease", json={
                    "text": symptoms,
                    "age":  age if age else None,
                    "sex":  sex if sex else None
                })
                data = res.json()

                st.markdown(f"""
                <div class="result-card">
                    <h3>Diagnosis</h3>
                    <p>{data.get("explanation", "")}</p>
                </div>
                """, unsafe_allow_html=True)

                if data.get("raw_result", {}).get("diseases"):
                    st.subheader("Top Predictions")
                    for d in data["raw_result"]["diseases"]:
                        st.metric(
                            label=str(d.get("name", "")).title(),
                            value=f"{round(d.get('confidence', 0) * 100)}%"
                        )

                with st.expander("🔍 Full details"):
                    st.json(data)

                st.warning("⚠️ This is not a substitute for professional medical advice.")

            except Exception as e:
                st.error(f"Error: {e}")

# ── PAGE: LAB ANALYZER ────────────────────────────
elif page == "Lab Analyzer":

    test  = st.selectbox("Test", [
        "hemoglobin", "glucose_fasting", "hba1c",
        "creatinine", "wbc", "platelets",
        "tsh", "sodium", "potassium",
        "total_cholesterol", "ldl", "hdl",
        "alt", "ast", "total_bilirubin",
        "bun", "calcium", "triglycerides"
    ])
    value = st.number_input("Value", min_value=0.0, step=0.1)
    sex   = st.selectbox("Sex (optional)", ["", "male", "female"])

    if st.button("Analyze"):
        with st.spinner("Interpreting..."):
            try:
                res  = requests.post(f"{API_URL}/analyze/lab", json={
                    "test_name": test,
                    "value":     value,
                    "sex":       sex if sex else None
                })
                data   = res.json()
                status = data.get("result", {}).get("status", "")

                color = (
                    "#ef4444" if "HIGH" in status
                    else "#f59e0b" if "LOW" in status
                    else "#22c55e"
                )

                st.markdown(f"""
                <div class="result-card" style="border-left: 4px solid {color};">
                    <h3 style="color:{color};">{status}</h3>
                    <p>{data.get("explanation", "")}</p>
                    <p><b>Normal Range:</b> {data.get("result", {}).get("normal_range", "N/A")}
                    {data.get("result", {}).get("unit", "")}</p>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("🔍 Full details"):
                    st.json(data)

                st.warning("⚠️ This is not a substitute for professional medical advice.")

            except Exception as e:
                st.error(f"Error: {e}")

# ── PAGE: MEDICAL Q&A ─────────────────────────────
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
elif page == "Medical Q&A":

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
<<<<<<< HEAD
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:12px; margin-bottom:10px;">
=======
        css_class = "chat-user" if msg["role"] == "You" else "chat-ai"
        st.markdown(f"""
        <div class="{css_class}">
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
            <b>{msg["role"]}</b><br>{msg["content"]}
        </div>
        """, unsafe_allow_html=True)

<<<<<<< HEAD
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
=======
    q = st.text_input("Ask a medical question")

    if st.button("Send") and q:
        st.session_state.chat.append({"role": "You", "content": q})
        with st.spinner("Searching knowledge base..."):
            try:
                res = requests.post(f"{API_URL}/qa", json={"question": q})
                ans = res.json().get("explanation", "No answer found.")
                st.session_state.chat.append({"role": "AI", "content": ans})
            except Exception as e:
                st.session_state.chat.append({"role": "AI", "content": f"Error: {e}"})
        st.rerun()

# ── PAGE: UPLOAD REPORT ───────────────────────────
elif page == "Upload Report":

    file = st.file_uploader("Upload medical report", type=["png", "jpg", "jpeg", "pdf"])

    if file:
        if file.type.startswith("image"):
            st.image(file, caption="Uploaded Report", use_column_width=True)

        if st.button("Analyze"):
            with st.spinner("Extracting text..."):
                try:
                    res  = requests.post(
                        f"{API_URL}/ocr",
                        files={"file": (file.name, file.getvalue(), file.type)}
                    )
                    data = res.json()

                    extracted = data.get("result", {}).get("extracted_text", "")

                    st.markdown(f"""
                    <div class="result-card">
                        <h3>Extracted Text</h3>
                        <pre style="white-space:pre-wrap;">{extracted if extracted else "No text extracted yet — OCR module coming soon"}</pre>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("🔍 Full details"):
                        st.json(data)

                except Exception as e:
                    st.error(f"Error: {e}")
>>>>>>> 8a08d43580701720e3982bfc2749087e46ff4c54
