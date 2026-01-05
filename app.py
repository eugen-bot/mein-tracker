import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- KONFIGURATION ---
st.set_page_config(page_title="Supplement Coach", page_icon="💊", layout="centered")

# --- CSS FÜR HANDY-OPTIMIERUNG ---
st.markdown("""
    <style>
    .stCheckbox { padding: 10px; border-radius: 5px; background-color: #f0f2f6; margin-bottom: 5px; }
    .big-font { font-size:20px !important; font-weight: bold; }
    .success-msg { color: green; font-weight: bold; padding: 10px; border: 1px solid green; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- DATEN: DEIN OPTIMIERTER PLAN ---
def get_default_plan():
    return {
        "PRIO (Arzt)": [
            {"name": "Valsamtrio", "dosis": "Nach Anweisung", "info": "Blutdrucksenker. Morgens!"}
        ],
        "Morgens (Frühstück)": [
            {"name": "Magnesium-Orotat", "dosis": "3 Kapseln", "info": "105 mg Mg (Gall Pharma)"},
            {"name": "Vitamin D3 + K2", "dosis": "Individuell (Tropfen)", "info": "Benötigt Fett! (NaturElan)"},
            {"name": "Ginkgo + B-Komplex", "dosis": "1 Tablette", "info": "Kreislauf & Fokus (Vroody)"},
            {"name": "Taurin", "dosis": "1-2 Kapseln", "info": "Optional für Energie"}
        ],
        "Mittags (Hauptmahlzeit)": [
            {"name": "Magnesium Taurate", "dosis": "4 Kapseln", "info": "160 mg Mg"},
            {"name": "Zink Bisglycinat", "dosis": "1 Tablette", "info": "NICHT nüchtern nehmen! (Pro Fuel)"},
            {"name": "Omega-3 1400", "dosis": "1 Kapsel", "info": "Herzschutz (Doppelherz)"},
            {"name": "Coenzym Q10", "dosis": "1 Kapsel", "info": "Zellenergie (Robert Franz)"}
        ],
        "Abends (Abendessen)": [
            {"name": "Mg Bisglycinat", "dosis": "3 Kapseln", "info": "Entspannung (Pro Fuel)"},
            {"name": "Chrom 500", "dosis": "1 Tablette", "info": "Blutzucker (Vit4Ever)"}
        ],
        "Nachts (Vor dem Schlafen)": [
            {"name": "Mg Night + Melatonin", "dosis": "1 Beutel", "info": "Direct Granulat"},
            {"name": "GABA", "dosis": "4 Kapseln", "info": "Viel Wasser trinken"},
            {"name": "Baldrian Forte", "dosis": "1 Dragee", "info": "Beruhigung (Abtei)"},
            {"name": "Mg L-Threonat", "dosis": "2 Kapseln", "info": "Gehirngängig"}
        ]
    }

# --- SESSION STATE INITIALISIEREN ---
if 'history' not in st.session_state:
    st.session_state.history = {} 
if 'date' not in st.session_state:
    st.session_state.date = date.today()

# Reset Logik: Wenn ein neuer Tag ist, Checkboxen leeren
if st.session_state.date != date.today():
    st.session_state.history = {} 
    st.session_state.date = date.today()

# --- HAUPT-APP ---
st.title("💊 Mein Supplement Plan")
st.caption(f"Datum: {date.today().strftime('%d.%m.%Y')}")

# Prioritäts-Warnung
st.warning("⚠️ **WICHTIG:** Valsamtrio (Blutdruck) hat Vorrang!")

plan = get_default_plan()
all_done_count = 0
total_items = sum(len(items) for items in plan.values())

# Tabs für Übersicht
tab1, tab2 = st.tabs(["✅ Heute Abhaken", "📊 Statistik"])

with tab1:
    completed_today = 0
    
    for category, items in plan.items():
        with st.expander(f"**{category}**", expanded=True):
            for item in items:
                # Eindeutiger Key für jede Checkbox
                key = f"{category}_{item['name']}"
                
                # Checkbox rendern
                is_checked = st.checkbox(
                    f"**{item['name']}** ({item['dosis']})",
                    key=key,
                    help=item['info']
                )
                
                if item['info']:
                    st.caption(f"ℹ️ {item['info']}")
                
                if is_checked:
                    completed_today += 1

    # Fortschrittsbalken
    if total_items > 0:
        progress = completed_today / total_items
        st.progress(progress)
        
        if progress == 1.0:
            st.balloons()
            st.success("🎉 Alles erledigt für heute! Starke Leistung.")

with tab2:
    st.subheader("Deine Disziplin")
    st.info("Hier erscheint deine Statistik, sobald wir die Datenbank verbunden haben.")
    
    # Demo Chart
    chart_data = pd.DataFrame({
        'Tag': ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'],
        'Erfüllung': [80, 90, 100, 85, 100, 95, 100]
    })
    st.bar_chart(chart_data, x='Tag', y='Erfüllung')

# Footer
st.markdown("---")
st.caption("Version 1.0 | Optimierter Plan | Baden-Württemberg Edition")
