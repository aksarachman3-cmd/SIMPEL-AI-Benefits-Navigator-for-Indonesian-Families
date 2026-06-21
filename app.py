import streamlit as st
import joblib
import numpy as np
from lang import strings

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="SIMPEL", page_icon="🧭", layout="centered")

# ---------- PRINT STYLES ----------
st.markdown("""
<style>
@media print {
  /* Hide everything by default */
  body * {
    visibility: hidden;
  }
  /* Show only the print area and its contents */
  #print-area, #print-area * {
    visibility: visible;
  }
  /* Position the print area at the top left */
  #print-area {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 20px;
  }
  /* Force all expanders to be fully opened when printing */
  .streamlit-expanderContent {
    display: block !important;
  }
  /* Make the expander header visible as well */
  .streamlit-expanderHeader {
    visibility: visible;
  }
}
</style>
""", unsafe_allow_html=True)

# ---------- LANGUAGE SETUP ----------
if 'lang' not in st.session_state:
    st.session_state.lang = 'id'

# Language selector in a compact top-right column
_, lang_col = st.columns([5, 1])
with lang_col:
    lang = st.selectbox(
        strings[st.session_state.lang]["lang_label"],
        ["id", "en"],
        format_func=lambda x: "🇮🇩 Bahasa Indonesia" if x == "id" else "🇬🇧 English",
        key="lang_selector",
        on_change=lambda: st.session_state.update(lang=st.session_state.lang_selector)
    )
    st.session_state.lang = lang

t = strings[lang]

# ---------- LOAD MODEL & ENCODER (cached) ----------
@st.cache_resource
def load_model():
    model = joblib.load("model/model.pkl")
    encoder = joblib.load("model/encoder.pkl")
    return model, encoder

try:
    model, encoder = load_model()
    model_loaded = True
except Exception as e:
    st.error("Gagal memuat model. Pastikan file model.pkl dan encoder.pkl ada di folder model/")
    model_loaded = False

# ---------- HEADER ----------
st.title(t["title"])
st.caption("SIMPEL is a hackathon prototype. Not an official government tool. Built for USAII's Global AI Hackathon 2026.")
st.markdown(t["subtitle"])
st.caption(t["caption"])

# ---------- PROGRAM DETAILS (from language dictionary) ----------
program_info = t["program_info"]

# ---------- QUESTIONNAIRE ----------
# Original Indonesian option strings (used internally for model mapping)
income_options_id = ["< Rp500.000", "Rp500.000 – Rp1.000.000", "Rp1.000.000 – Rp2.000.000", "> Rp2.000.000"]
family_options_id = ["1", "2", "3", "4", "5 atau lebih"]
wall_options_id = ["Tembok", "Semi permanen (setengah tembok)", "Papan/kayu", "Bambu/lainnya"]
yes_no_id = ["Ya", "Tidak"]

# Translated display lists
income_display = t["income_options"]
family_display = t["family_options"]
wall_display = t["wall_options"]
yes_no_display = [t["yes"], t["no"]]

pendapatan = st.selectbox(
    t["q1"],
    income_options_id,
    format_func=lambda x: income_display[income_options_id.index(x)]
)

jumlah_anggota = st.selectbox(
    t["q2"],
    family_options_id,
    format_func=lambda x: family_display[family_options_id.index(x)]
)

anak_sekolah = st.radio(
    t["q3"],
    yes_no_id,
    format_func=lambda x: t["yes"] if x == "Ya" else t["no"]
)

anak_balita = st.radio(
    t["q4"],
    yes_no_id,
    format_func=lambda x: t["yes"] if x == "Ya" else t["no"]
)

lansia = st.radio(
    t["q5"],
    yes_no_id,
    format_func=lambda x: t["yes"] if x == "Ya" else t["no"]
)

disabilitas = st.radio(
    t["q6"],
    yes_no_id,
    format_func=lambda x: t["yes"] if x == "Ya" else t["no"]
)

dinding_rumah = st.selectbox(
    t["q7"],
    wall_options_id,
    format_func=lambda x: wall_display[wall_options_id.index(x)]
)

# ---------- BUTTON & AI PREDICTION ----------
if st.button(t["btn"], type="primary"):
    if not model_loaded:
        st.error("Model AI tidak tersedia. Periksa kembali folder model/.")
    else:
        # Map the text responses to numbers (must match training data)
        income_map = {
            "< Rp500.000": 0,
            "Rp500.000 – Rp1.000.000": 1,
            "Rp1.000.000 – Rp2.000.000": 2,
            "> Rp2.000.000": 3
        }
        anggota_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5 atau lebih": 5}
        dinding_map = {
            "Tembok": 0,
            "Semi permanen (setengah tembok)": 1,
            "Papan/kayu": 2,
            "Bambu/lainnya": 3
        }

        # Create an array of 7 features
        features = np.array([
            income_map[pendapatan],
            anggota_map[jumlah_anggota],
            1 if anak_sekolah == "Ya" else 0,
            1 if anak_balita == "Ya" else 0,
            1 if lansia == "Ya" else 0,
            1 if disabilitas == "Ya" else 0,
            dinding_map[dinding_rumah]
        ]).reshape(1, -1)

        # Multi-label probability prediction
        proba = model.predict_proba(features)

        # Collect programs with a probability of ≥ 0.5
        program_list = []
        confidences = {}
        program_names = list(encoder.classes_)

        for i, prog in enumerate(program_names):
            if proba[i][0][1] >= 0.5:
                program_list.append(prog)
                raw_conf = proba[i][0][1]
                confidences[prog] = min(raw_conf, 0.95)

        # Arrange the programs in a natural order: PKH, BPNT, PIP, PBI_JKN
        urutan = ["PKH", "BPNT", "PIP", "PBI_JKN"]
        program_list = [p for p in urutan if p in program_list]

        # ---------- PRINT AREA START ----------
        st.markdown('<div id="print-area">', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader(t["result_title"])

        if not program_list:
            st.warning(t["no_result"])
        else:
            st.success(t["success_msg"].format(len(program_list)))

            for prog in program_list:
                info = program_info[prog]
                conf = confidences[prog]

                with st.expander(f"✅ {info['nama']} – {t['why']} {conf:.0%}"):
                    st.markdown(f"**{t['why']}** {info['alasan']}")
                    st.markdown(f"**{t['desc']}:** {info['deskripsi']}")
                    st.markdown(f"**{t['docs']}:**")
                    docs = info['dokumen'].split(', ')
                    for doc in docs:
                        st.markdown(f"- {doc}")
                    st.markdown(f"**{t['place']}:** {info['tempat']}")
                    st.markdown(f"**{t['source']}:** {info['sumber']}")

        st.markdown("---")

        # ---------- DISCLAIMER ----------
        st.warning(t["disclaimer"])

        # ---------- PRINTING TIPS ----------
        st.info(t["print_tip"])

        st.markdown('</div>', unsafe_allow_html=True)
        # ---------- PRINT AREA END ----------

        # ---------- RESET BUTTON (outside print area) ----------
        if st.button(t["reset"]):
            st.rerun()
