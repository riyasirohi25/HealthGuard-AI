import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="HealthGuard AI",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 HealthGuard AI")
st.caption("AI-powered medical assistant — not a substitute for professional medical advice")

page = st.sidebar.selectbox("Choose Module", [
    "Disease Predictor",
    "Lab Analyzer",
    "Medical Q&A",
    "Upload Report (OCR)"
])

# ── Disease Predictor ─────────────────────────
if page == "Disease Predictor":
    st.header("Disease Predictor")
    st.write("Enter your symptoms below and the AI will predict possible conditions.")

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="e.g. fever, headache, sore throat, fatigue"
    )
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age (optional)", min_value=0, max_value=120, value=0)
    with col2:
        sex = st.selectbox("Sex (optional)", ["", "male", "female"])

    if st.button("Analyze Symptoms", type="primary"):
        if not symptoms.strip():
            st.warning("Please enter your symptoms first")
        else:
            with st.spinner("Analyzing symptoms..."):
                try:
                    res = requests.post(f"{API_URL}/predict/disease", json={
                        "text": symptoms,
                        "age": age if age > 0 else None,
                        "sex": sex if sex else None
                    })
                    data = res.json()
                    st.success("Analysis complete")
                    st.subheader("Results")
                    st.write("**Explanation:**", data.get("explanation"))

                    diseases = data.get("result", {}).get("diseases", [])
                    if diseases:
                        for d in diseases:
                            st.metric(
                                label=d.get("name", "Unknown").title(),
                                value=f"{round(d.get('confidence', 0) * 100)}% confidence"
                            )
                    else:
                        st.info("No diseases predicted yet — model not connected")

                    st.warning(data.get("disclaimer"))

                except Exception as e:
                    st.error(f"Could not connect to API: {e}")
                    st.info("Make sure backend is running: python -m uvicorn api.main:app --reload")

# ── Lab Analyzer ──────────────────────────────
elif page == "Lab Analyzer":
    st.header("Lab Report Analyzer")
    st.write("Enter your lab test results to get an instant interpretation.")

    col1, col2 = st.columns(2)
    with col1:
        test = st.selectbox("Select Test", [
            "hemoglobin", "glucose_fasting", "hba1c",
            "creatinine", "wbc", "platelets",
            "tsh", "sodium", "potassium",
            "total_cholesterol", "ldl", "hdl",
            "alt", "ast", "total_bilirubin",
            "bun", "calcium", "triglycerides"
        ])
        value = st.number_input("Enter Value", min_value=0.0, step=0.1, format="%.2f")
        sex = st.selectbox("Sex (optional)", ["", "male", "female"])

    with col2:
        st.write("")
        st.write("")
        if st.button("Interpret Result", type="primary"):
            with st.spinner("Interpreting..."):
                try:
                    res = requests.post(f"{API_URL}/analyze/lab", json={
                        "test_name": test,
                        "value": value,
                        "sex": sex if sex else None
                    })
                    data = res.json()
                    status = data.get("result", {}).get("status", "")

                    if status == "HIGH":
                        st.error(f"Status: {status} ⬆")
                    elif status == "LOW":
                        st.warning(f"Status: {status} ⬇")
                    elif status == "NORMAL":
                        st.success(f"Status: {status} ✓")
                    elif status == "CRITICALLY LOW" or status == "CRITICALLY HIGH":
                        st.error(f"🚨 {status} — Seek immediate medical attention")
                    else:
                        st.info(f"Status: {status}")

                    st.write("**Explanation:**", data.get("explanation"))
                    st.write("**Normal Range:**", data.get("result", {}).get("normal_range", "N/A"))
                    st.write("**Unit:**", data.get("result", {}).get("unit", "N/A"))
                    st.warning(data.get("disclaimer"))

                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

# ── Medical Q&A ───────────────────────────────
elif page == "Medical Q&A":
    st.header("Medical Q&A")
    st.write("Ask any medical question and get an answer from the knowledge base.")

    question = st.text_input(
        "Your question",
        placeholder="e.g. What is the normal range for blood sugar?"
    )

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Please enter a question")
        else:
            with st.spinner("Searching knowledge base..."):
                try:
                    res = requests.post(f"{API_URL}/qa", json={"question": question})
                    data = res.json()
                    st.subheader("Answer")
                    st.write(data.get("explanation"))
                    sources = data.get("sources", [])
                    if sources:
                        st.caption("Sources: " + ", ".join(sources))
                    st.warning(data.get("disclaimer"))
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")

# ── OCR Upload ────────────────────────────────
elif page == "Upload Report (OCR)":
    st.header("Upload Medical Report")
    st.write("Upload a scanned report or image and the system will extract and analyze the text.")

    uploaded = st.file_uploader(
        "Upload report",
        type=["png", "jpg", "jpeg", "pdf"]
    )

    if uploaded:
        if uploaded.type.startswith("image"):
            st.image(uploaded, caption="Uploaded Report", use_column_width=True)

        if st.button("Extract & Analyze", type="primary"):
            with st.spinner("Processing..."):
                try:
                    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                    res = requests.post(f"{API_URL}/ocr", files=files)
                    data = res.json()
                    st.subheader("Extracted Text")
                    extracted = data.get("result", {}).get("extracted_text", "")
                    if extracted:
                        st.text_area("Result", extracted, height=200)
                    else:
                        st.info("OCR module not yet connected")
                    st.warning(data.get("disclaimer"))
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")