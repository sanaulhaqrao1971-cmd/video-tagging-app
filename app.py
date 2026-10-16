import streamlit as st
import whisper
import tempfile
import os
import re
from collections import Counter

# Page Configuration
st.set_page_config(
    page_title="24 News Channel Unlimited Tagging System", 
    page_icon="📺", 
    layout="wide"
)

# Professional Corporate Dashboard Custom CSS Styling
st.markdown("""
    <style>
    /* Background & Main App */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    h1 {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 2.4rem;
        letter-spacing: -0.5px;
    }
    h3 {
        color: #38bdf8 !important;
    }
    .upload-text {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 1.5rem;
    }

    /* File Uploader Container & Labels Fix */
    div[data-testid="stFileUploader"] {
        background-color: #1e293b;
        border: 2px dashed #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #38bdf8;
    }
    
    /* Upload Label Text Color Fix (ویڈیو فائل اپ لوڈ کریں - Title Fix) */
    div[data-testid="stFileUploader"] label, 
    div[data-testid="stWidgetLabel"] p,
    .stFileUploader label p {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Upload Box Subtext (200MB per file...) */
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span {
        color: #94a3b8 !important;
    }
    
    /* Upload Button Inside Widget */
    div[data-testid="stFileUploader"] button {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* Main Action Button Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        border: none;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.5);
        transform: translateY(-1px);
    }
    
    /* Output Box */
    pre {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #38bdf8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📺 24 News Channel Unlimited Local Tagging System")
st.markdown('<p class="upload-text">100% Free & Unlimited video tagging using local AI (Whisper). No API limits!</p>', unsafe_allow_html=True)

# Load Local Whisper Model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")

with st.spinner("لوکل اے آئی ماڈل لوڈ ہو رہا ہے... براہ کرم انتظار کریں۔"):
    ai_model = load_whisper_model()

# Video Uploader Widget
uploaded_file = st.file_uploader("ویڈیو فائل اپ لوڈ کریں (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    if st.button("انگریزی ٹیگز تیار کریں (Generate Tags)"):
        with st.spinner("ویڈیو کو لوکللی پروسیس کیا جا رہا ہے..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                # Whisper کے ذریعے آڈیو کو ٹیکسٹ میں بدلنا
                result = ai_model.transcribe(tmp_file_path)
                transcript_text = result.get("text", "")

                # ٹیکسٹ سے خودکار اہم انگریزی الفاظ نکالنا
                words = re.findall(r'\b[A-Za-z]{4,}\b', transcript_text)
                stop_words = {"this", "that", "with", "from", "your", "have", "will", "what", "about", "there", "the", "and", "for", "are", "but", "not", "you", "all", "can", "was", "they", "one", "has", "her", "his", "were", "been"}
                filtered_words = [w.lower() for w in words if w.lower() not in stop_words]
                
                common_words = [word for word, count in Counter(filtered_words).most_common(12)]
                tags_string = ", ".join(common_words)

                st.success("ٹیگز کامیابی سے تیار ہو گئے ہیں!")
                
                st.markdown("### 📝 جنریٹ شدہ ٹیگز:")
                st.code(tags_string, language="text")

                with st.expander("مکمل آڈیو ٹرانسکرپٹ دیکھیں"):
                    st.write(transcript_text)

            except Exception as e:
                st.error(f"پروسیسنگ میں خرابی: {e}")

            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
