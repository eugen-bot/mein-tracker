import streamlit as st
import pandas as pd
from datetime import date
import google.generativeai as genai
from PIL import Image

# --- KONFIGURATION ---
st.set_page_config(page_title="Supplement Coach AI", page_icon="💊", layout="centered")

# API Key laden (aus den Secrets)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    else:
        st.error("Kein API-Key gefunden! Bitte in den Streamlit Settings eintragen.")
except Exception:
    pass # Fehler ignorieren beim lokalen Test ohne Secrets

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stCheckbox { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px; }
    .big-font { font-size:20px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- DATEN & STATE ---
def get_default_plan():
    # Dein Basis-Plan
    return {
        "PRIO (Arzt)": [{"name": "Valsamtrio", "dosis": "Nach Anweisung", "info": "Blutdrucksenker. Morgens!"}],
        "Morgens": [
            {"name": "Magnesium-Orotat", "dosis": "3 Kapseln", "info": "105 mg Mg"},
            {"name": "Vitamin D3 + K2", "dosis": "Individuell", "info": "Benötigt Fett!"},
            {"name": "Ginkgo + B-Komplex", "dosis": "1 Tablette", "info": "Kreislauf"}
        ],
        "Mittags": [
            {"name": "Magnesium Taurate", "dosis": "4 Kapseln", "info": "160 mg Mg"},
            {"name": "Zink Bisglycinat", "dosis": "1 Tablette", "info": "Zum Essen!"},
            {"name": "Omega-3", "dosis": "1 Kapsel", "info": "Herzschutz"}
        ],
        "Abends": [{"name": "Mg Bisglycinat", "dosis": "3 Kapseln", "info": "Entspannung"}],
        "Nachts": [
            {"name": "GABA", "dosis": "4 Kapseln", "info": "Mit viel Wasser"},
            {"name": "Baldrian", "dosis": "1 Dragee", "info": "Beruhigung"}
        ]
    }

# Session State initialisieren
if 'plan' not in st.session_state:
    st.session_state.plan = get_default_plan()

# --- KI FUNKTION ---
def analyze_image(image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    Analysiere dieses Foto eines Nahrungsergänzungsmittels.
    Antworte NUR in diesem Format:
    Name: [Produktname]
    Dosis: [Empfohlene Dosis laut Packung]
    Zeit: [Empfohlene Tageszeit: Morgens, Mittags, Abends oder Nachts]
    Info: [Kurzer Wirkstoff oder Hinweis]
    """
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Fehler bei der Analyse: {e}"

# --- HAUPT-APP ---
st.title("💊 Supplement Coach AI")

# Tabs
tab1, tab2, tab3 = st.tabs(["✅ Plan", "📸 Neu Scannen", "📊 Statistik"])

# TAB 1: DER PLAN
with tab1:
    st.caption(f"Heute: {date.today().strftime('%d.%m.%Y')}")
    completed_count = 0
    
    # Durchlaufe den gespeicherten Plan
    for category, items in st.session_state.plan.items():
        with st.expander(f"**{category}**", expanded=True):
            for item in items:
                key = f"{category}_{item['name']}"
                if st.checkbox(f"**{item['name']}** ({item['dosis']})", key=key, help=item.get('info', '')):
                    completed_count += 1
    
    st.progress(min(completed_count / 15, 1.0)) # Einfacher Balken

# TAB 2: KI SCANNER
with tab2:
    st.header("Neues Mittel hinzufügen")
    st.info("Mache ein Foto der Verpackung (Vorderseite oder Rückseite mit Dosierung).")
    
    img_file = st.camera_input("Foto machen")
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Dein Foto", width=200)
        
        with st.spinner("KI analysiert Verpackung..."):
            # KI Analyse aufrufen
            result_text = analyze_image(image)
            st.success("Analyse fertig!")
            st.code(result_text, language="yaml")
            st.warning("Hinweis: Die automatische Eintragung in den Plan folgt im nächsten Update!")

# TAB 3: STATISTIK
with tab3:
    st.subheader("Deine Disziplin")
    # Demo Chart
    chart_data = pd.DataFrame({'Tag': ['Mo', 'Di', 'Mi', 'Do', 'Fr'], 'Treue': [80, 90, 100, 85, 100]})
    st.bar_chart(chart_data, x='Tag', y='Treue')
