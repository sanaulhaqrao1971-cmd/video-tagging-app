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
        margin-bottom: 1.0rem;
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
        with st.spinner("Processing video & generating scene tags..."):
            file_name = uploaded_file.name
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            try:
                # Whisper کے ذریعے آڈیو ٹرانسکرپشن
                result = ai_model.transcribe(tmp_file_path)
                transcript_text = result.get("text", "").strip()

                # فائل کے نام سے الفاظ نکالنا (جیسے case, florida وغیرہ)
                name_words = re.findall(r'[A-Za-z]+', file_name.replace('.mp4', '').replace('.mov', ''))
                
                # آڈیو ٹیکسٹ سے الفاظ نکالنا
                audio_words = re.findall(r'\b[A-Za-z]{3,}\b', transcript_text)
                stop_words = {"this", "that", "with", "from", "your", "have", "will", "what", "about", "there", "the", "and", "for", "are", "but", "not", "you", "all", "can", "was", "they", "one", "has", "her", "his", "were", "been", "mp4"}
                
                combined_words = name_words + audio_words
                filtered_words = [w.lower() for w in combined_words if w.lower() not in stop_words and len(w) > 2]
                
                if filtered_words:
                    common_words = [word for word, count in Counter(filtered_words).most_common(12)]
                    # نیوز چینل کے لحاظ سے سمارٹ کی ورڈز کا اضافہ
                    news_tags = ["breaking news", "report", "24 news archive"]
                    final_tags = list(dict.fromkeys(common_words + news_tags))
                    tags_string = ", ".join(final_tags[:15])
                else:
                    tags_string = "breaking news, news update, video report, 24 news archive, current affairs"

                st.success("Tags generated successfully! Copy the tags from the box below.")
                
                st.markdown("### Generated Tags (Ready to Copy):")
                st.code(tags_string, language="text")

                with st.expander("View Full Audio Transcript & Details"):
                    st.write(f"**File Name Analyzed:** {file_name}")
                    st.write(f"**Audio Transcript:** {transcript_text if transcript_text else 'No distinct speech detected in audio track.'}")

            except Exception as e:
                st.error(f"Processing error: {e}")

            finally:
                if os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)
