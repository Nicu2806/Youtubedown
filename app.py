import streamlit as st
import yt_dlp
import os
import time

st.set_page_config(page_title="YouTube Downloader Sigur", page_icon="🔊")

st.title("🔊 YouTube Downloader (Video + Audio)")
st.write("Acest script descarcă versiunea gata unită (Video cu Sunet).")

url = st.text_input("Lipește link-ul YouTube aici:")

DOWNLOAD_FOLDER = "Downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def download_video_safe(link):
    # Folosim timestamp pentru a fi siguri că nu încurcăm fișierele vechi cu cele noi
    timestamp = int(time.time())
    
    ydl_opts = {
        # SCHIMBARE MAJORA: 'best' în loc de 'bestvideo+bestaudio'
        # Asta forțează descărcarea singurului fișier care le conține pe ambele.
        'format': 'best', 
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s_{timestamp}.%(ext)s',
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
        video_title = info.get('title', 'video')
        
        # Descărcăm
        ydl.download([link])
        
        # Calculăm numele fișierului final
        # yt-dlp returnează extensia corectă (de obicei mp4) automat
        filename = ydl.prepare_filename(info)
        
        return filename, video_title

if st.button("Descarcă ACUM"):
    if not url:
        st.warning("Pune un link!")
    else:
        try:
            with st.spinner('⏳ Se descarcă (Video + Audio)...'):
                file_path, title = download_video_safe(url)
            
            # Verificăm dacă fișierul chiar există înainte să zicem gata
            if os.path.exists(file_path):
                st.success(f"✅ GATA! Fișier unic descărcat: {title}")
                
                # Deschidem fișierul pentru butonul de download din browser
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="📥 Ia fișierul (Video cu Sunet) pe PC",
                        data=file,
                        file_name=os.path.basename(file_path),
                        mime="video/mp4"
                    )
            else:
                st.error("Eroare: Fișierul nu a fost găsit după descărcare.")
                
        except Exception as e:
            st.error(f"A apărut o eroare: {e}")
