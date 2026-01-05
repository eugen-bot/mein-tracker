import streamlit as st
import pandas as pd
from datetime import date
from google import genai
from PIL import Image

# --- KONFIGURATION ---
st.set_page_config(page_title="Supplement Coach", page_icon="💊", layout="centered")

# --- STYLING ---
st.markdown("""
    <style>
    .stCheckbox { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- DATEN: DEIN PLAN ---
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

# --- DATEN: PLAN FÜR KATHARINA ---
def get_plan_katharina():
    # Hier kannst du Katharinas echte Mittel eintragen
    return {
        "Morgens": [
            {"name": "Multivitamin", "dosis": "1 Tablette", "info": "Basis-Versorgung"},
            {"name": "Eisen + C", "dosis": "1 Tablette", "info": "Bei Bedarf"}
        ],
        "Abends": [
            {"name": "Magnesium", "dosis": "2 Kapseln", "info": "Entspannung"}
        ]
    }

# --- SIDEBAR: PROFIL WAHL ---
st.sidebar.header("Benutzerprofil")
# Jetzt mit Katharina statt Freund
user = st.sidebar.radio("Wer nutzt die App?", ["Eugen", "Katharina"])

# Session State Logik für Benutzerwechsel
if 'current_user' not in st.session_state:
    st.session_state.current_user = user

if st.session_state.current_user != user:
    st.session_state.current_user = user
    # Plan neu laden basierend auf Auswahl
    if user == "Eugen":
        st.session_state.plan = get_plan_eugen()
    else:
        st.session_state.plan = get_plan_katharina()
    st.rerun()

# Initiales Laden
if 'plan' not in st.session_state:
    if user == "Eugen":
        st.session_state.plan = get_plan_eugen()
    else:
        st.session_state.plan = get_plan_katharina()

# --- FUNKTIONEN ---
def delete_item(category, item_name):
    st.session_state.plan[category] = [i for i in st.session_state.plan[category] if i['name'] != item_name]
    st.rerun()

def analyze_image(image):
    if "GOOGLE_API_KEY" not in st.secrets:
        return "Fehler: Kein API Key in den Secrets gefunden."
    
    # Nutzung der neuen google-genai Bibliothek
    try:
        client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[image, "Analysiere dieses Supplement. Antworte kurz: Name, Dosis, Zeit."]
        )
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
                    # Der Key enthält jetzt "Katharina", damit ihre Haken eigenständig sind
                    key = f"{user}_{category}_{item['name']}"
                    st.checkbox(f"**{item['name']}** ({item['dosis']})", key=key, help=item.get('info', ''))

with tab2:
    st.header("Neu hinzufügen")
    st.info(f"Füge ein Mittel zum Plan von **{user}** hinzu.")
    img_file = st.camera_input("Foto machen")
    if img_file:
        image = Image.open(img_file)
        st.image(image, width=200)
        with st.spinner("Analysiere..."):
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
