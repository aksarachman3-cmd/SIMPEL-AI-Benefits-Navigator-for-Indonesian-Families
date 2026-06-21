<p align="center">
  <img src="docs/screenshots/logo.png" alt="SIMPEL Logo" width="200"/>
</p>

# SIMPEL – AI Benefits Navigator for Indonesian Families

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://simpel.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**SIMPEL** (Sistem Informasi Mudah Pahami Eligibility Layanan) is an AI‑powered tool that asks **7 simple questions** about a household and instantly predicts which of Indonesia’s four largest national social programs they may qualify for — complete with plain‑language explanations, confidence scores, required documents, and the nearest government office to visit.

> **"Satu Langkah, Semua Bantuan."**  
> *One step, all assistance.*

---

## 🎥 Demo & Resources

| Resource | Link |
|----------|------|
| **🟢 Live Web App** | [Streamlit Cloud](https://simpel.streamlit.app/) |
| **📓 Jupyter Notebook** | [eligibility_classifier.ipynb](jupyter/eligibility_classifier.ipynb) |
| **🎨 Figma Prototype** | [View on Figma](https://seven-five-38917158.figma.site) *(static mockup – not connected to AI)* |
| **📹 Video Walkthrough** | [YouTube (unlisted)](https://youtu.be/igHWbig9Zew?si=0p7M_vpV0PqD5_gE) |
| **📸 Documentation & Screenshots** | [docs/README.md](docs/README.md) |

---

## 🇮🇩 Programs Covered

SIMPEL screens for four national social assistance programs:

| Program | Full Name | What It Provides |
|---------|-----------|------------------|
| **PKH** | Program Keluarga Harapan | Conditional cash transfers for families with pregnant women, school‑age children, elderly, or disabled members |
| **BPNT** | Bantuan Pangan Non‑Tunai | Monthly food assistance (Rp200,000) for purchasing staple foods at designated e‑warong (government‑appointed local shops) |
| **PIP** | Program Indonesia Pintar | Cash assistance for school‑age children (elementary to high school, SD–SMA) from low‑income families to cover educational expenses |
| **PBI‑JKN** | Penerima Bantuan Iuran – Jaminan Kesehatan Nasional | Free health insurance with premiums paid by the government |

---

## ❓ Problem
Over eight million of low‑income Indonesian families miss out on cash transfers, food assistance, school aid, and free healthcare every year — not because they are ineligible, but because eligibility rules are fragmented across different government websites, written in bureaucratic language, and impossible to interpret under stress. Families who qualify do not apply simply because they do not know where to start.

*Sources: World Bank (2023) — Indonesia Social Assistance Review; TNP2K (2022) — coverage gap analysis.*

---

## 💡 Solution
SIMPEL asks **7 plain‑language questions** (in Bahasa Indonesia), then uses a **multi‑label Random Forest classifier** trained on synthetic data to predict which national social programs a family may qualify for. The output includes:
- ✅ Program names with confidence scores (capped at 95%)
- 📝 Plain‑language explanations of why the model suggests each program
- 📄 A ready‑to‑print document checklist
- 📍 The exact government office to visit
- ⚠️ A persistent yellow disclaimer reminding users that this is a simulation, not an official decision

---

## 🛠️ Key Features
- 🧭 **Guided questionnaire** – no chatbot; designed for low‑literacy users and slow 2G/3G networks
- 🤖 **AI reasoning** – interpretable multi‑label Random Forest with feature importance
- 🛡️ **Responsible AI** – always uses *“mungkin”* (may qualify) language; confidence capped at 95%; human‑in‑the‑loop mandatory
- 🖨️ **Print‑ready** – results can be printed and taken directly to the kelurahan (village office)
- 👥 **Kader‑friendly** – can be operated by community helpers on behalf of families without smartphones
- 🌐 **Bilingual interface** – Bahasa Indonesia and English toggle; judges can read the UI in English

---

## 🏗️ Architecture & Technical Decisions

- **No paid APIs, no external LLM calls.** The app runs entirely on a free Streamlit Cloud instance. The Random Forest model (`model.pkl`, ~2 MB) is loaded once into memory and all predictions happen locally in under 10 ms. No internet connection is needed for inference after the initial page load.
- **Static model – deliberate, not a bug.** The model was trained on simplified eligibility rules from official sources (Kemensos, BPJS, Kemdikbud) and does **not** auto‑update when government policies change. We deliberately chose this approach because the Indonesian government does not provide public APIs for real‑time eligibility data, and official websites are frequently unavailable — exactly the infrastructure challenge our users face. Instead, the app always provides direct links to official sources so users can manually verify the latest rules. The app is transparent that results are a simulation and must be verified at the kelurahan (village office).
- **Deterministic & interpretable.** Every prediction can be explained with feature importance. The output is never “you definitely qualify” – always *“Anda mungkin memenuhi syarat”* (you may qualify). Confidence is capped at 95% to prevent over‑reliance.

---

## 🧠 AI Architecture

- **Input:** 7 multiple‑choice answers (income bracket, family size, presence of school child, toddler/pregnancy, elderly, disability, wall material), each mapped to an ordinal or binary numeric feature.  
- **AI capability:** Multi‑label classification via a Random Forest (scikit‑learn `MultiOutputClassifier`, 100 trees, max‑depth=5). One input can produce multiple simultaneous program recommendations.  
- **Processing:** The 7‑feature vector is passed to `predict_proba()`; each of the four binary estimators returns a probability. A threshold of ≥0.5 selects likely programs. Displayed confidence is capped at 95%.  
- **Outputs:** A list of programs (PKH, BPNT, PIP, PBI‑JKN) with confidence score, plain‑language explanation, required documents checklist, and the exact government office to visit. Model is loaded once in RAM via Streamlit caching; inference <10 ms with zero external API calls.  
- **Evaluation:** Validated on a held‑out test set (F1 0.95–0.99) and manually stress‑tested with edge cases (wealthy households, elderly alone).

---

## 📊 Data
All data is **100% synthetic** (4,273 households), generated programmatically based on simplified official eligibility rules from:
- [Kemensos – PKH](https://www.kemensos.go.id/program-keluarga-harapan-pkh)
- [Kemensos – BPNT](https://www.kemensos.go.id/bantuan-pangan-non-tunai-bpnt)
- [Kemendikbud – PIP](https://pip.kemendikdasmen.go.id/home_v1)
- [BPJS Kesehatan – PBI](https://www.bpjs-kesehatan.go.id/#/)

To improve fairness and avoid over‑prediction, we added 5% label noise and included 1,500 negative samples (clearly ineligible households).

---

## 🛡️ Responsible AI Guardrails

- **Human‑in‑the‑Loop:** The AI never makes the final eligibility determination. It only suggests programs; actual enrollment is decided by government officers at the kelurahan or Dinas Sosial.
- **Over‑reliance prevention:** Confidence is capped at 95%, and every result screen carries a permanent yellow disclaimer: *“Ini bukan keputusan resmi. Harap verifikasi ke kelurahan.”*
- **Privacy by design:** The app stores absolutely nothing — a page refresh or tab close wipes all session data.

---

## ⚠️ Limitations & Scalability

- **Free‑tier deployment:** The live demo runs on Streamlit Cloud’s free tier, which supports a limited number of concurrent users. For production use, the app can be trivially moved to a paid Streamlit Cloud plan, Hugging Face Spaces, or a self‑hosted container (Docker) without code changes.
- **Single‑file architecture:** Because the entire app is one Python file, scaling horizontally is straightforward – simply spin up more identical instances behind a load balancer. The model file is tiny and CPU‑only; no GPU or cloud‑specific service is required.
- **No persistent data:** The app does not store any user information, so no database or privacy‑heavy infrastructure is needed. This also means no user‑specific history; each session is independent.

---

## 📴 Offline Roadmap (Technical)

We plan to make SIMPEL fully offline by compiling the scikit‑learn model to pure JavaScript using [m2cgen](https://github.com/BayesWitnesses/m2cgen). The pipeline:

1. Convert the trained `RandomForestClassifier` into a standalone JavaScript function (no Python required).
2. Embed that function in a static HTML page together with the questionnaire UI.
3. Bundle as a Progressive Web App (PWA) so the entire tool can be installed on a phone and run without any internet connection – even on 2G‑only devices.

This approach eliminates the need for a backend entirely and makes SIMPEL viable in the most remote areas.

---

## 🧰 Tech Stack
- **Full Stack:** [Streamlit](https://streamlit.io/) (Python) – single‑file web application
- **ML:** [scikit‑learn](https://scikit-learn.org/) (Random Forest, MultiOutputClassifier)
- **Data:** [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualization:** [Matplotlib](https://matplotlib.org/)
- **Model Persistence:** [joblib](https://joblib.readthedocs.io/)
- **Development:** [Jupyter Notebook](https://jupyter.org/), [Google Colab](https://colab.research.google.com/)
- **Design:** [Figma](https://figma.com/)
- **Deployment:** [Streamlit Cloud](https://streamlit.io/cloud) (free tier)
- **Version Control:** [GitHub](https://github.com/)

---

## 🗺️ What’s Next

- **Voice input** – integrate Web Speech API (online) or Vosk (offline) for illiterate users.
- **Multi‑language** – extend the language dictionary to Javanese, Sundanese, etc.
- **WhatsApp integration** – lightweight Flask webhook + WhatsApp Business Cloud API.
- **DTKS (Data Terpadu Kesejahteraan Sosial – Indonesia's official social welfare database) sync** – periodically fetch official welfare data into a local SQLite cache for offline‑first verification.
- **Fully offline PWA** – compile model → JavaScript, bundle with static UI (see Offline Roadmap above).
- **Guardrailed chatbot** – a fine‑tuned small model (e.g., Gemma 2B) sandboxed to answer only program‑related questions.

---

## 🚀 How to Run Locally

```bash
# Clone the repository
git clone https://github.com/[ALIF_USERNAME]/simpel.git
cd simpel

# (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
