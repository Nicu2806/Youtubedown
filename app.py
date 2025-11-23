import streamlit as st
import subprocess
import os

# --- Configurare pagină Streamlit ---
st.set_page_config(
    page_title="YouTube Downloader (yt-dlp)",
    layout="centered"
)

DOWNLOAD_DIR = "youtube_downloads"

# --- Funcția principală de descărcare ---
def download_video_ytdlp(url, format_choice):
    """
    Descarcă un videoclip folosind yt-dlp.
    """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Parametrii de bază
    base_command = [
        "yt-dlp",
        "--output", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"), # Definește calea și numele fișierului
        url
    ]

    # Ajustează comanda în funcție de alegere
    if format_choice == "video":
        # Cea mai bună calitate video/audio combinată
        command = base_command + ["-f", "bestvideo+bestaudio/best"]
        success_msg = "Descărcare video completă finalizată!"
    
    elif format_choice == "audio":
        # Descarcă doar audio și convertește în mp3
        command = base_command + ["-x", "--audio-format", "mp3"]
        success_msg = "Descărcare audio MP3 finalizată!"

    try:
        # Rulare comanda yt-dlp
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Extragerea numelui fișierului descărcat din output
        # yt-dlp scrie calea finală în stdout
        file_name_search = [line for line in process.stdout.splitlines() if "[ExtractAudio]" in line or "[download]" in line]
        
        # O metodă simplă de a găsi calea (necesită o mică prelucrare a output-ului)
        if file_name_search:
             # Căutăm linia care indică destinația finală
             final_line = [line for line in file_name_search if "Destination:" in line or "has been merged" in line][-1]
             
             # Încercăm să extragem calea exactă
             if "Destination:" in final_line:
                 file_path = final_line.split("Destination: ")[1].strip()
             elif "has been merged" in final_line:
                 # Când videoul e descărcat din bucăți și fuzionat (cel mai comun)
                 # Calea este între ghilimele: "Calea/numele_fisierului.mp4"
                 try:
                    path_part = final_line.split(" to ")[1].strip()
                    file_path = path_part.strip('"')
                 except IndexError:
                    file_path = None
             else:
                file_path = None
        else:
            file_path = None # Nu s-a putut determina calea

        return f"✅ {success_msg}", file_path
    
    except subprocess.CalledProcessError as e:
        error_output = e.stderr
        st.error(f"❌ yt-dlp a returnat o eroare: {error_output[:500]}...") # Afișează primele 500 de caractere
        return f"❌ Eroare la descărcare: {e.returncode}", None
    except Exception as e:
        return f"❌ A apărut o eroare necunoscută: {e}", None

# --- Interfața Streamlit ---
st.title("⬇️ YouTube Downloader folosind yt-dlp")
st.markdown("Folosește biblioteca **yt-dlp** pentru descărcări mai stabile și mai rapide.")

url_input = st.text_input("Adresa URL a videoclipului YouTube", placeholder="Ex: https://www.youtube.com/watch?v=...")

quality_options = {
    "Cea mai bună calitate video (MP4)": "video",
    "Doar audio (MP3)": "audio"
}
selected_quality_label = st.selectbox("Alegeți formatul de descărcare", list(quality_options.keys()))
format_code = quality_options[selected_quality_label]

if st.button("Descarcă", type="primary"):
    if url_input:
        with st.spinner('Procesare și descărcare în curs...'):
            message, file_path = download_video_ytdlp(url_input, format_code)
            
            st.markdown(message)
            
            if file_path and os.path.exists(file_path):
                file_name = os.path.basename(file_path)
                
                # Citirea fișierului pentru descărcarea Streamlit
                try:
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"Click pentru a descărca **{file_name}**",
                            data=file,
                            file_name=file_name,
                            mime="application/octet-stream"
                        )
                    st.success(f"Fișierul **{file_name}** a fost generat și este gata de descărcare.")
                except Exception as e:
                    st.error(f"Eroare la generarea link-ului de descărcare: {e}")
                    
            elif "Eroare" not in message:
                 st.warning("Descărcarea a reușit, dar nu s-a putut localiza fișierul final pentru a genera link-ul de descărcare.")

    else:
        st.warning("Vă rugăm să introduceți o adresă URL validă.")