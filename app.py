import streamlit as st
import google.generativeai as genai

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="PlanCraft AI - Asisten Penata Jadwal",
    page_icon="📅",
    layout="wide"
)

# Sidebar: Pengaturan Parameter Kreatif
st.sidebar.title("⚙️ Parameter Asisten")
st.sidebar.markdown("Atur konfigurasi asisten produktivitas kamu:")

api_key = st.sidebar.text_input("Google Gemini API Key:", type="password", help="Masukkan API Key dari Google AI Studio")

tone = st.sidebar.selectbox(
    "Gaya Bahasa (Tone):",
    ["Ramah & Suportif", "Strict & Disiplin", "Santai & Kasual"]
)

output_format = st.sidebar.selectbox(
    "Format Output Utama:",
    ["Timeline Per Jam", "Checklist To-Do List", "Matriks Prioritas (Penting vs Santai)"]
)

temperature = st.sidebar.slider(
    "Kreativitas/Keluwesan (Temperature):",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1
)

if st.sidebar.button("🧹 Hapus Riwayat Chat"):
    st.session_state.messages = []
    st.rerun()

# Tampilan Utama
st.title("📅 PlanCraft AI")
st.subheader("Asisten Penata Jadwal & Agenda Cerdas")
st.write(f"**Gaya Bahasa:** *{tone}* | **Format Utama:** *{output_format}*")

if not api_key:
    st.info("💡 Silakan masukkan **Gemini API Key** kamu di sidebar sebelah kiri untuk memulai.")
    st.stop()

genai.configure(api_key=api_key)

system_instruction = f"""
Kamu adalah PlanCraft AI, seorang asisten produktivitas dan penata jadwal pribadi yang cerdas dan efisien.

Aturan Respon:
1. Gaya Bahasa: Gunakan penyampaian yang {tone}.
2. Format Penyusunan: Utamakan tampilan dalam format {output_format} saat merapikan jadwal atau tugas pengguna.
3. Tugas Utama:
   - Mengubah catatan aktivitas acak pengguna menjadi jadwal yang terstruktur dan realistis.
   - Memberikan estimasi durasi dan pengingat/persiapan penting untuk setiap agenda.
   - Mengusulkan alokasi waktu istirahat yang seimbang.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tuliskan aktivitas atau agenda kamu hari ini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=system_instruction,
            generation_config={"temperature": temperature}
        )

        formatted_history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]

        chat = model.start_chat(history=formatted_history)

        with st.chat_message("assistant"):
            with st.spinner("PlanCraft AI sedang merapikan agenda kamu..."):
                response = chat.send_message(prompt)
                st.markdown(response.text)

        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses permintaan: {e}")
