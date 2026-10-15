import streamlit as st
from google import genai
import tempfile
import os

st.set_page_config(page_title="24 News Channel Video Tagging System", layout="wide")
st.title("📺 24 News Channel Video Metadata & Tagging System")
st.write("ویڈیو اپلوڈ کریں، خودکار ٹیگز کاپی کریں اور اپنے لوکل آرکائیو میں محفوظ کریں۔")

# Streamlit Secrets سے API Key حاصل کرنا
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("اپنی Google Gemini API Key درج کریں:", type="password")

if api_key:
    clean_api_key = api_key.strip()
    
    try:
        client = genai.Client(api_key=clean_api_key)
        
        uploaded_file = st.file_uploader("ویڈیو فائل اپلوڈ کریں (MP4, MOV, AVI)", type=["mp4", "mov", "avi"])

        if uploaded_file is not None:
            st.video(uploaded_file)
            
            prompt = st.text_area(
                "پرامپٹ (Prompt):", 
                "Provide a detailed summary, key topics, English timestamps, and relevant tags for this TV video clip for 24 News archive cataloging."
            )

            if st.button("میٹا ڈیٹا اور ٹیگز بنائیں"):
                with st.spinner("ویڈیو اپلوڈ اور پروسیس ہو رہی ہے..."):
                    # 1. ٹیمپریری فائل بنانا
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name

                    video_file = None
                    try:
                        # 2. گوگل سرور پر اپلوڈ
                        video_file = client.files.upload(file=tmp_file_path)
                        
                        # 3. ٹیگز اور میٹا ڈیٹا کی تیاری
                        response = client.models.generate_content(
                            model='gemini-3.5-flash',
                            contents=[video_file, prompt]
                        )

                        st.success("تجزیہ مکمل ہو گیا! نیچے دیے گئے باکس سے ٹیگز کاپی کریں۔")
                        
                        # 4. کاپی کرنے کے لیے آسان باکس
                        st.markdown("### 📝 تیار شدہ میٹا ڈیٹا و ٹیگز (کاپی کرنے کے لیے):")
                        st.code(response.text, language="text")

                    except Exception as inner_e:
                        st.error(f"پروسیسنگ کا ایرر: {inner_e}")

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
        st.error(f"API Key کنفیگریشن کا ایرر: {e}")
else:
    st.warning("براہ کرم Streamlit Secrets میں GEMINI_API_KEY شامل کریں یا سائیڈ بار میں درج کریں۔")
