import streamlit as st
import pandas as pd
from datetime import date
import google.generativeai as genai
from PIL import Image

# --- KONFIGURATION ---
st.set_page_config(page_title="Supplement Coach AI", page_icon="💊", layout="centered")

# API Key laden (falls vorhanden)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass 

# --- STYLING ---
st.markdown("""
    <style>
    .stCheckbox { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px; }
    .delete-btn { color: red; border-color: red; }
    </style>
""", unsafe_allow_html=True)

# --- DATEN: DER START-PLAN ---
def get_default_plan():
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
            {"name": "Omega-3", "dosis": "1 Kapsel", "info": "Herzschutz"},
            {"name": "Coenzym Q10", "dosis": "1 Kapsel", "info": "Zellenergie"}
        ],
        "Abends": [
            {"name": "Mg Bisglycinat", "dosis": "3 Kapseln", "info": "Entspannung"},
            {"name": "Chrom 500", "dosis": "1 Tablette", "info": "Blutzucker"}
        ],
        "Nachts": [
            {"name": "Mg Night + Melatonin", "dosis": "1 Beutel", "info": "Granulat"},
            {"name": "GABA", "dosis": "4 Kapseln", "info": "Viel Wasser"},
            {"name": "Baldrian", "dosis": "1 Dragee", "info": "Beruhigung"},
            {"name": "Mg L-Threonat", "dosis": "2 Kapseln", "info": "Gehirn"}
        ]
    }

# Session State initialisieren (Plan laden)
if 'plan' not in st.session_state:
    st.session_state.plan = get_default_plan()

# --- FUNKTIONEN ---
def delete_item(category, item_name):
    # Löscht ein Element aus der Liste
    st.session_state.plan[category] = [i for i in st.session_state.plan[category] if i['name'] != item_name]
    st.rerun()

def analyze_image(image):
    # KI Funktion
    if "GOOGLE_API_KEY" not in st.secrets:
        return "Fehler: Kein API Key hinterlegt."
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    Analysiere dieses Foto eines Nahrungsergänzungsmittels.
    Antworte kurz im Format:
    Name: [Produktname]
    Dosis: [Empfohlene Dosis]
    Zeit: [Tageszeit]
    """
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Fehler: {e}"

# --- HAUPT-APP ---
st.title("💊 Supplement Coach")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["✅ Plan", "📸 Scan", "📊 Stats", "⚙️ Einstellungen"])

# TAB 1: DER PLAN
with tab1:
    st.caption(f"Heute: {date.today().strftime('%d.%m.%Y')}")
    
    for category, items in st.session_state.plan.items():
        if items: # Nur anzeigen wenn nicht leer
            with st.expander(f"**{category}**", expanded=True):
                for item in items:
                    key = f"chk_{category}_{item['name']}"
                    st.checkbox(f"**{item['name']}** ({item['dosis']})", key=key, help=item.get('info', ''))

# TAB 2: SCANNER
with tab2:
    st.header("Neu hinzufügen")
    img_file = st.camera_input("Foto machen")
    if img_file:
        image = Image.open(img_file)
        st.image(image, width=200)
        with st.spinner("Analysiere..."):
            st.info(analyze_image(image))

# TAB 3: STATISTIK
with tab3:
    st.subheader("Übersicht")
    chart_data = pd.DataFrame({'Tag': ['Mo', 'Di', 'Mi', 'Do', 'Fr'], 'Treue': [80, 90, 100, 85, 100]})
    st.bar_chart(chart_data, x='Tag', y='Treue')

# TAB 4: EINSTELLUNGEN (LÖSCHEN)
with tab4:
    st.header("Plan bearbeiten")
    st.info("Hier kannst du Mittel aus deinem Tagesplan entfernen.")
    
    for category, items in st.session_state.plan.items():
        if items:
            st.subheader(category)
            for item in items:
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['name']}**")
                
                # Der Lösch-Button
                if col2.button("🗑️", key=f"del_{item['name']}"):
                    delete_item(category, item['name'])
