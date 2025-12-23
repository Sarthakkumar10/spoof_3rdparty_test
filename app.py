import streamlit as st
import requests

st.set_page_config(page_title="Liveness Detection", layout="centered")

API_URL = "https://neuroverify.neuraldefend.com/detect/liveness"
API_KEY = st.secrets["API_KEY"]

st.title("🧠 Liveness Detection")

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)

def badge_color(tag):
    if tag == "REAL":
        return "#28a745"   # green
    elif tag == "SPOOF":
        return "#dc3545"   # red
    else:
        return "#ffc107"   # yellow

if uploaded_file and st.button("Run Liveness Check"):
    st.image(uploaded_file, use_column_width=True)

    with st.spinner("Analyzing image..."):
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        headers = {
            "x-api-key": API_KEY
        }
        resp = requests.post(API_URL, headers=headers, files=files)

    if resp.status_code != 200:
        st.error(f"API Error: {resp.status_code}")
    else:
        data = resp.json()
        analysis = data.get("image_analysis", {})

        tag = analysis.get("prediction_tag", "UNKNOWN")

        st.markdown(
            f"""
            <div style="
                padding:14px;
                border-radius:10px;
                background:{badge_color(tag)};
                color:white;
                font-size:24px;
                font-weight:bold;
                text-align:center;
            ">
                {tag}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("📄 Full Response")
        st.json(data)
