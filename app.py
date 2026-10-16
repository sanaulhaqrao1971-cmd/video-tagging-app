import streamlit as st
from google import genai
import tempfile
import os
import time

# Page Configuration
st.set_page_config(
    page_title="24 News Channel Video Tagging System", 
    page_icon="📺", 
    layout="wide"
)

# Professional Corporate Dashboard Custom CSS Styling
st.markdown("""
    <style>
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
    textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
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
    pre {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #38bdf8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("📺 24 News Channel Video Metadata & Tagging System")
st.markdown('<p class="upload-text">Upload video, get automated English tags instantly, and save them to your local archive.</p>', unsafe_allow_html=True)

# Streamlit Secrets سے API Key حاصل کرنا
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter your Google Gemini API Key:", type="password")

if api_key:
    clean_api_key = api_key.strip()
    
    try:
        client = genai.Client(api_key=clean_api_key)
        
        uploaded_file = st.file_uploader("Upload video file (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

        if uploaded_file is not None:
            st.video(uploaded_file)
            
            # پرامپٹ
            prompt = st.text_area(
                "Prompt:", 
                "Generate only comma-separated relevant tags in English for this TV video clip for 24 News archive cataloging. Do not include any summary, key topics, or timestamps."
            )

            if st.button("Generate English Tags"):
                with st.spinner("Processing video & managing rate limits..."):
                    # 1. ٹیمپریری فائل بنانا
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                    video_file = None
                    try:
                        # 2. گوگل سرور پر اپلوڈ
                        video_file = client.files.upload(file=tmp_file_path)
                        
                        # 3. سمارٹ ری ٹرائی لوپ جو 503 اور 429 (Quota) दोनों को ہینڈل کرے گا
                        response = None
                        max_retries = 5
                        for attempt in range(max_retries):
                            try:
                                response = client.models.generate_content(
                                    model='gemini-3.8-flash',
                                    contents=[video_file, prompt]
                                )
                                break
                            except Exception as e:
                                error_str = str(e)
                                if ("503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "RESOURCE_EXHAUSTED" in error_str) and attempt < max_retries - 1:
                                    sleep_time = (attempt + 1) * 6 # کوٹہ یا بزی ہونے پر زیادہ انتظار (6, 12, 18, 24 سیکنڈ)
                                    time.sleep(sleep_time)
                                else:
                                    raise e

                        st.success("Tags generated successfully! Copy the tags from the box below.")
                        
                        # 4. کاپی کرنے کے لیے آسان باکس
                        st.markdown("### 📝 Generated Tags (Ready to Copy):")
                        st.code(response.text, language="text")

                    except Exception as inner_e:
                        st.error(f"Processing error: {inner_e}")

                    finally:
                        # 5. خودکار صفائی
                        if video_file:
                            try:
                                client.files.delete(name=video_file.name)
                            except Exception:
                                pass
                        
                        if os.path.exists(tmp_file_path):
                            os.remove(tmp_file_path)

    except Exception as e:
        st.error(f"API Key configuration error: {e}")
else:
    st.warning("Please add GEMINI_API_KEY in Streamlit Secrets or enter it in the sidebar.")
