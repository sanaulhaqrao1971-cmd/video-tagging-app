
import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="TV Archive Video Tagging System", layout="wide")

st.title("📺 TV Channel Video Metadata & Tagging System")
st.write("Google Gemini 1.5 Flash AI کی مدد سے اپنی ویڈیوز کا خودکار میٹا ڈیٹا اور ٹیگز تیار کریں۔")

# API Key Setup
api_key = st.sidebar.text_input("اپنی Google Gemini API Key درج کریں:", type="password")

if api_key:
    clean_api_key = api_key.strip()
    genai.configure(api_key=clean_api_key)
    
    uploaded_file = st.file_uploader("ویڈیو فائل اپلوڈ کریں (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

    if uploaded_file is not None:
        st.video(uploaded_file)
        
        prompt = st.text_area(
            "پرامپٹ (Prompt):", 
            "Provide a detailed summary, key topics, Urdu timestamps, and relevant tags for this TV video clip for archive cataloging."
        )

        if st.button("میٹا ڈیٹا اور ٹیگز بنائیں"):
            with st.spinner("ویڈیو کا تجزیہ کیا جا رہا ہے... براہ کرم انتظار کریں..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name

                try:
                    video_file = genai.upload_file(path=tmp_file_path)
                    
                    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                    response = model.generate_content([video_file, prompt])

                    st.success("تجزیہ مکمل ہو گیا!")
                    st.markdown("### 📝 تیار شدہ میٹا ڈیٹا:")
                    st.write(response.text)

                    os.remove(tmp_file_path)

                except Exception as e:
                    st.error(f"ایرر آ گیا: {e}")
else:
    st.info("براہ کرم سائیڈ بار میں اپنی Gemini API Key درج کریں۔")
