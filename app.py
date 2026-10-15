import streamlit as st
from google import genai
import tempfile
import os
import time

st.set_page_config(page_title="24 News Channel Video Tagging System", layout="wide")
st.title("📺 24 News Channel Video Metadata & Tagging System")
st.write("Upload video, get automated English tags instantly, and save them to your local archive.")

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
                with st.spinner("Uploading and processing video..."):
                    # 1. ٹیمپریری فائل بنانا
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                    video_file = None
                    try:
                        # 2. گوگل سرور پر اپلوڈ
                        video_file = client.files.upload(file=tmp_file_path)
                        
                        # 3. آٹو ری ٹرائی لاجک (تاکہ سرور بزی ہونے پر ایرر نہ آئے)
                        response = None
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                response = client.models.generate_content(
                                    model='gemini-3.8-flash',
                                    contents=[video_file, prompt]
                                )
                                break
                            except Exception as e:
                                if "503" in str(e) and attempt < max_retries - 1:
                                    time.sleep(3) # 3 سیکنڈ انتظار کر کے دوبارہ کوشش کرے گا
                                else:
                                    raise e

                        st.success("Tags generated successfully! Copy the tags from the box below.")
                        
                        # 4. کاپی کرنے کے لیے آسان باکس
                        st.markdown("### 📝 Generated Tags (Ready to Copy):")
                        st.code(response.text, language="text")

                    except Exception as inner_e:
                        st.error(f"Processing error: {inner_e}")

                    finally:
                        # 5. خودکار صفائی (سرور اور لوکل دونوں جگہ سے ویڈیو ڈیلیٹ کرنا)
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
