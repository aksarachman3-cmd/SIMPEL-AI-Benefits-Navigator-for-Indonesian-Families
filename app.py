import streamlit as st
import joblib
import numpy as np
from lang import strings

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="SIMPEL", page_icon="🧭", layout="centered")

# ---------- LANGUAGE SETUP ----------
if 'lang' not in st.session_state:
    st.session_state.lang = 'id'

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

# ---------- PROGRAM DETAILS ----------
program_info = t["program_info"]

# ---------- QUESTIONNAIRE ----------
income_options_id = ["< Rp500.000", "Rp500.000 – Rp1.000.000", "Rp1.000.000 – Rp2.000.000", "> Rp2.000.000"]
family_options_id = ["1", "2", "3", "4", "5 atau lebih"]
wall_options_id = ["Tembok", "Semi permanen (setengah tembok)", "Papan/kayu", "Bambu/lainnya"]
yes_no_id = ["Ya", "Tidak"]

income_display = t["income_options"]
family_display = t["family_options"]
wall_display = t["wall_options"]
yes_no_display = [t["yes"], t["no"]]

pendapatan = st.selectbox(t["q1"], income_options_id, format_func=lambda x: income_display[income_options_id.index(x)])
jumlah_anggota = st.selectbox(t["q2"], family_options_id, format_func=lambda x: family_display[family_options_id.index(x)])
anak_sekolah = st.radio(t["q3"], yes_no_id, format_func=lambda x: t["yes"] if x == "Ya" else t["no"])
anak_balita = st.radio(t["q4"], yes_no_id, format_func=lambda x: t["yes"] if x == "Ya" else t["no"])
lansia = st.radio(t["q5"], yes_no_id, format_func=lambda x: t["yes"] if x == "Ya" else t["no"])
disabilitas = st.radio(t["q6"], yes_no_id, format_func=lambda x: t["yes"] if x == "Ya" else t["no"])
dinding_rumah = st.selectbox(t["q7"], wall_options_id, format_func=lambda x: wall_display[wall_options_id.index(x)])

# ---------- BUTTON & AI PREDICTION ----------
if st.button(t["btn"], type="primary"):
    if not model_loaded:
        st.error("Model AI tidak tersedia. Periksa kembali folder model/.")
    else:
        income_map = {
            "< Rp500.000": 0, "Rp500.000 – Rp1.000.000": 1,
            "Rp1.000.000 – Rp2.000.000": 2, "> Rp2.000.000": 3
        }
        anggota_map = {"1": 1, "2": 2, "3": 3, "4": 4, "5 atau lebih": 5}
        dinding_map = {"Tembok": 0, "Semi permanen (setengah tembok)": 1, "Papan/kayu": 2, "Bambu/lainnya": 3}

        features = np.array([
            income_map[pendapatan], anggota_map[jumlah_anggota],
            1 if anak_sekolah == "Ya" else 0,
            1 if anak_balita == "Ya" else 0,
            1 if lansia == "Ya" else 0,
            1 if disabilitas == "Ya" else 0,
            dinding_map[dinding_rumah]
        ]).reshape(1, -1)

        proba = model.predict_proba(features)

        program_list, confidences = [], {}
        program_names = list(encoder.classes_)
        for i, prog in enumerate(program_names):
            if proba[i][0][1] >= 0.5:
                program_list.append(prog)
                confidences[prog] = min(proba[i][0][1], 0.95)

        urutan = ["PKH", "BPNT", "PIP", "PBI_JKN"]
        program_list = [p for p in urutan if p in program_list]

        # ---------- DISPLAY RESULTS ON SCREEN ----------
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
                    for doc in info['dokumen'].split(', '):
                        st.markdown(f"- {doc}")
                    st.markdown(f"**{t['place']}:** {info['tempat']}")
                    st.markdown(f"**{t['source']}:** {info['sumber']}")

        st.markdown("---")
        st.warning(t["disclaimer"])
        st.info(t["print_tip"])

        # ---------- BUILD HTML STRING FOR DOWNLOAD ----------
        html_content = f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="UTF-8"><title>Hasil SIMPEL</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; color: #000; }}
  h2 {{ color: #1E90FF; }}
  .card {{ border: 1px solid #ccc; border-radius: 8px; padding: 15px; margin-bottom: 12px; }}
  .card h3 {{ margin-top: 0; color: #10B981; }}
  .disclaimer {{ margin-top: 20px; padding: 12px; background: #FFF3CD; border-left: 4px solid #F59E0B; }}
  .print-tip {{ color: #666; font-style: italic; margin-top: 10px; }}
  .doc-list {{ padding-left: 20px; }}
</style>
</head>
<body>
<h2>{t["result_title"]}</h2>
"""
        if not program_list:
            html_content += f"<p>{t['no_result']}</p>"
        else:
            html_content += f"<p><strong>{t['success_msg'].format(len(program_list))}</strong></p>"
            for prog in program_list:
                info = program_info[prog]
                conf = confidences[prog]
                html_content += f"""
<div class="card">
  <h3>✅ {info['nama']} — {t['why']} {conf:.0%}</h3>
  <p><strong>{t['why']}</strong> {info['alasan']}</p>
  <p><strong>{t['desc']}:</strong> {info['deskripsi']}</p>
  <p><strong>{t['docs']}:</strong></p>
  <ul class="doc-list">
"""
                for doc in info['dokumen'].split(', '):
                    html_content += f"    <li>{doc}</li>\n"
                html_content += f"""  </ul>
  <p><strong>{t['place']}:</strong> {info['tempat']}</p>
  <p><strong>{t['source']}:</strong> {info['sumber']}</p>
</div>
"""
        html_content += f"""
<div class="disclaimer">
  <strong>⚠️ {t['disclaimer'].replace('**', '').replace('*', '')}</strong>
</div>
<div class="print-tip">{t['print_tip']}</div>
</body></html>
"""

        st.download_button(
            label=t["download_btn"],
            data=html_content,
            file_name="simpel-result.html",
            mime="text/html",
        )

        # ---------- RESET BUTTON ----------
        if st.button(t["reset"]):
            st.rerun()