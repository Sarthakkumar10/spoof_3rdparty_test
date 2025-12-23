import streamlit as st
import requests
from PIL import Image, ImageOps
import io

st.set_page_config(
    page_title="Liveness Detection",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API_URL = "https://neuroverify.neuraldefend.com/detect/liveness"
API_KEY = st.secrets["API_KEY"]

# ------------------ UI HEADER ------------------
st.markdown(
    """
    <h2 style="text-align:center;">🧠 Liveness Detection</h2>
    <p style="text-align:center; color:gray;">
        Upload an image or capture using camera to detect spoof / real face
    </p>
    """,
    unsafe_allow_html=True
)

# ------------------ INPUT MODE ------------------
input_mode = st.radio(
    "Choose input method",
    ["📤 Upload Image", "📷 Use Camera"],
    horizontal=True
)

# ------------------ HELPERS ------------------
def badge_color(tag):
    return {
        "REAL": "#28a745",
        "SPOOF": "#dc3545"
    }.get(tag, "#ffc107")

def fix_image_rotation(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image)  # 🔥 fixes rotation
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer

def call_liveness_api(image_buffer, filename="image.jpg"):
    files = {
        "file": (filename, image_buffer, "image/jpeg")
    }
    headers = {
        "x-api-key": API_KEY
    }
    return requests.post(API_URL, headers=headers, files=files, timeout=15)

# ------------------ UPLOAD FLOW ------------------
if input_mode == "📤 Upload Image":
    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file and st.button("Run Liveness Check", use_container_width=True):
        fixed_img = fix_image_rotation(uploaded_file.getvalue())

        st.image(fixed_img, use_column_width=True)

        with st.spinner("Analyzing image..."):
            resp = call_liveness_api(fixed_img, uploaded_file.name)

# ------------------ CAMERA FLOW ------------------
else:
    camera_image = st.camera_input("Capture image")

    if camera_image:
        fixed_img = fix_image_rotation(camera_image.getvalue())

        st.image(fixed_img, use_column_width=True)

        with st.spinner("Analyzing image..."):
            resp = call_liveness_api(fixed_img)

# ------------------ RESPONSE HANDLING ------------------
if "resp" in locals():
    if resp.status_code != 200:
        st.error(f"API Error: {resp.status_code}")
    else:
        data = resp.json()
        analysis = data.get("image_analysis", {})

        tag = analysis.get("prediction_tag", "UNKNOWN")
        confidence = analysis.get("liveness_check", {}).get("confidence", 0)

        # ------------------ RESULT CARD ------------------
        st.markdown(
            f"""
            <div style="
                margin-top:20px;
                padding:20px;
                border-radius:14px;
                background:{badge_color(tag)};
                color:white;
                text-align:center;
                font-size:26px;
                font-weight:700;
            ">
                {tag}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------ CONFIDENCE ------------------
        st.metric(
            label="Liveness Confidence",
            value=f"{confidence * 100:.2f} %"
        )

        with st.expander("🔍 View Full API Response"):
            st.json(data)
