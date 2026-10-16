import streamlit as st
import whisper
import tempfile
import os
import re
from collections import Counter

# Page Configuration
st.set_page_config(
    page_title="24 News Channel Video Tagging System", 
    page_icon="📺", 
    layout="wide"
)

# Professional Light Theme Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    h1 {
        color: #0f172a !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 2.1rem;
    }
    .upload-text {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #ffffff;
        color: #0f172a;
        border: 1px solid #cbd5e1;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #f1f5f9;
        border-color: #94a3b8;
    }
    pre, code {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("24 News Channel Video Metadata & Tagging System")
st.markdown('<p class="upload-text">Upload video, get automated English tags instantly, and save them to your local archive.</p>', unsafe_allow_html=True)

# Load Local Whisper Model
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("tiny")

with st.spinner("لوکل اے آئی ماڈل لوڈ ہو رہا ہے..."):
    ai_model = load_whisper_model()

# Video Uploader
uploaded_file = st.file_uploader("Upload video file (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    st.video(uploaded_file)
    
    prompt = st.text_area(
        "Prompt:", 
        "Generate only comma-separated relevant tags in English for this TV video clip for 24 News archive cataloging. Do not include any summary, key topics, or timestamps."
    )

    if st.button("Generate English Tags"):
        with st.spinner("Processing video & generating tags..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                # Whisper کے ذریعے آڈیو کو ٹیکسٹ میں بدلنا
                result = ai_model.transcribe(tmp_file_path)
                transcript_text = result.get("text", "").strip()

                # اگر ٹرانسکرپٹ موجود ہو تو الفاظ نکالیں، ورنہ ڈیفالٹ ٹیگ دیں
                if transcript_text:
                    words = re.findall(r'\b[A-Za-z]{3,}\b', transcript_text)
                    stop_words = {"this", "that", "with", "from", "your", "have", "will", "what", "about", "there", "the", "and", "for", "are", "but", "not", "you", "all", "can", "was", "they", "one", "has", "her", "his", "were", "been"}
                    filtered_words = [w.lower() for w in words if w.lower() not in stop_words]
                    
                    if filtered_words:
                        common_words = [word for word, count in Counter(filtered_words).most_common(15)]
                        tags_string = ", ".join(common_words)
                    else:
                        tags_string = transcript_text
                else:
                    tags_string = "news, update, broadcast, video, archive"

                st.success("Tags generated successfully! Copy the tags from the box below.")
                
                st.markdown("### Generated Tags (Ready to Copy):")
                st.code(tags_string, language="text")

                with st.expander("View Full Audio Transcript"):
                    st.write(transcript_text if transcript_text else "No speech detected in audio.")

            except Exception as e:
                st.error(f"Processing error: {e}")

            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
