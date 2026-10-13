import streamlit as st
from google import genai
import tempfile
import os

st.set_page_config(page_title="TV Archive Video Tagging System", layout="wide")
st.title("📺 TV Channel Video Metadata & Tagging System")
st.write("Google Gemini 1.5 Flash AI کی مدد سے اپنی ویڈیوز کا خودکار میٹا ڈیٹا اور ٹیگز تیار کریں۔")

api_key = st.sidebar.text_input("اپنی Google Gemini API Key درج کریں:", type="password")

if api_key:
    clean_api_key = api_key.strip()
    
    try:
        # Initialize the new genai client
        client = genai.Client(api_key=clean_api_key)
        
        uploaded_file = st.file_uploader("ویڈیو فائل اپلوڈ کریں (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

        if uploaded_file is not None:
            st.video(uploaded_file)
            
            prompt = st.text_area(
                "پرامپٹ (Prompt):", 
                "Provide a detailed summary, key topics, Urdu timestamps, and relevant tags for this TV video clip for archive cataloging."
            )

            if st.button("میٹا ڈیٹا اور ٹیگز بنائیں"):
                with st.spinner("ویڈیو اپلوڈ اور تجزیہ کیا جا رہا ہے... براہ کرم انتظار کریں..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                    try:
                        # Upload file using the new files API
                        video_file = client.files.upload(file=tmp_file_path)
                        
                        # Generate content using gemini-2.5-flash or gemini-1.5-flash
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[video_file, prompt]
                        )

                        st.success("تجزیہ مکمل ہو گیا!")
                        st.markdown("### 📝 تیار شدہ میٹا ڈیٹا:")
                        st.write(response.text)

                        os.remove(tmp_file_path)

                    except Exception as inner_e:
                        st.error(f"پروسیسنگ کا ایرر: {inner_e}")

    except Exception as e:
        st.error(f"API Key کنفیگریشن کا ایرر: {e}")
else:
    st.info("براہ کرم سائیڈ بار میں اپنی Gemini API Key درج کریں۔")
