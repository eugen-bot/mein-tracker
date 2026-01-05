import streamlit as st
import pandas as pd
from datetime import date
import google.generativeai as genai
from PIL import Image

# --- KONFIGURATION ---
st.set_page_config(page_title="Supplement Coach", page_icon="💊", layout="centered")

# API Key laden
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass 

# --- STYLING ---
st.markdown("""
    <style>
    .stCheckbox { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- DATEN: HIER SIND DIE ZWEI PLÄNE ---

def get_plan_eugen():
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

def get_plan_freund():
    # HIER KANNST DU DIE MEDIKAMENTE DEINES FREUNDES EINTRAGEN
    return {
        "Morgens": [
            {"name": "Multivitamin", "dosis": "1 Tablette", "info": "Allgemein"},
            {"name": "Kaffee", "dosis": "1 Tasse", "info": "Wachmacher"}
        ],
        "Abends": [
            {"name": "Magnesium Sport", "dosis": "2 Kapseln", "info": "Nach dem Training"}
        ]
    }

# --- SIDEBAR: BENUTZER AUSWAHL ---
st.sidebar.header("Benutzerprofil")
user = st.sidebar.radio("Wer nutzt die App?", ["Eugen", "Freund"])

# Session State Reset bei Benutzerwechsel
if 'current_user' not in st.session_state:
    st.session_state.current_user = user

if st.session_state.current_user != user:
    st.session_state.current_user = user
    # Plan neu laden basierend auf Auswahl
    if user == "Eugen":
        st.session_state.plan = get_plan_eugen()
    else:
        st.session_state.plan = get_plan_freund()
    st.rerun()

# Initiales Laden beim allerersten Start
if 'plan' not in st.session_state:
    if user == "Eugen":
        st.session_state.plan = get_plan_eugen()
    else:
        st.session_state.plan = get_plan_freund()


# --- FUNKTIONEN ---
def delete_item(category, item_name):
    st.session_state.plan[category] = [i for i in st.session_state.plan[category] if i['name'] != item_name]
    st.rerun()

def analyze_image(image):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "Fehler: Kein API Key hinterlegt."
    
    # HIER IST DIE ÄNDERUNG: PRO STATT FLASH
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "Analysiere dieses Supplement. Antworte kurz: Name, Dosis, Zeit."
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Fehler: {e}"

# --- HAUPT-APP ---
st.title(f"💊 Plan für {user}")

tab1, tab2, tab3, tab4 = st.tabs(["✅ Plan", "📸 Scan", "📊 Stats", "⚙️ Einstellungen"])

with tab1:
    st.caption(f"Datum: {date.today().strftime('%d.%m.%Y')}")
    for category, items in st.session_state.plan.items():
        if items:
            with st.expander(f"**{category}**", expanded=True):
                for item in items:
                    key = f"{user}_{category}_{item['name']}" # Wichtig: User im Key trennt die Haken
                    st.checkbox(f"**{item['name']}** ({item['dosis']})", key=key, help=item.get('info', ''))

with tab2:
    st.header("Neu hinzufügen")
    st.info(f"Füge ein Mittel zum Plan von **{user}** hinzu.")
    img_file = st.camera_input("Foto machen")
    if img_file:
        image = Image.open(img_file)
        st.image(image, width=200)
        with st.spinner("Analysiere mit Gemini Pro..."):
            st.info(analyze_image(image))

with tab3:
    st.subheader("Statistik")
    st.bar_chart(pd.DataFrame({'Tag': ['Mo', 'Di'], 'Werte': [80, 95]}))

with tab4:
    st.header(f"Plan von {user} bearbeiten")
    for category, items in st.session_state.plan.items():
        if items:
            st.subheader(category)
            for item in items:
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{item['name']}**")
                if col2.button("🗑️", key=f"del_{user}_{item['name']}"):
                    delete_item(category, item['name'])
