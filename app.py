import streamlit as st
from groq import Groq

# ─── Sayfa ayarları ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NexusAI",
    page_icon="🤖",
    layout="centered",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Genel arka plan */
    .stApp {
        background-color: #0f0f1a;
    }

    /* Başlık alanı */
    .nexus-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .nexus-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #a78bfa;
        letter-spacing: 2px;
    }
    .nexus-subtitle {
        font-size: 0.95rem;
        color: #888;
        margin-top: 4px;
    }

    /* Kullanıcı mesajı */
    .msg-user {
        background: #3a3a5c;
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0 8px 15%;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* AI mesajı */
    .msg-ai {
        background: #1e1e2e;
        color: #e0e0e0;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px 15% 8px 0;
        font-size: 1rem;
        line-height: 1.5;
        border-left: 3px solid #a78bfa;
    }

    /* Zaman etiketi */
    .msg-time {
        font-size: 0.75rem;
        color: #666;
        margin-top: 4px;
    }

    /* Input alanı */
    .stTextInput input, .stTextArea textarea {
        background-color: #1e1e2e !important;
        color: white !important;
        border: 1px solid #3a3a5c !important;
        border-radius: 10px !important;
    }

    /* Buton */
    .stButton button {
        background-color: #7c3aed !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #6d28d9 !important;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #13131f !important;
    }

    /* Divider */
    hr {
        border-color: #2a2a3e;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f0f1a; }
    ::-webkit-scrollbar-thumb { background: #3a3a5c; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = "llama-3.1-8b-instant"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "Sen yardımcı bir yapay zeka asistanısın. Türkçe konuşuyorsun."

# ─── Sidebar (Ayarlar) ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    st.divider()

    api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_...",
        help="console.groq.com adresinden ücretsiz alabilirsiniz",
    )
    if api_key:
        st.session_state.api_key = api_key

    model = st.selectbox(
        "Model",
        options=[
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "gemma2-9b-it",
            "mixtral-8x7b-32768",
        ],
        index=0,
    )
    st.session_state.model = model

    system_prompt = st.text_area(
        "Sistem Promptu",
        value=st.session_state.system_prompt,
        height=100,
    )
    st.session_state.system_prompt = system_prompt

    st.divider()

    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div style='color: #666; font-size: 0.8rem; margin-top: 20px;'>
        Ücretsiz API key:<br>
        <a href='https://console.groq.com' target='_blank' style='color: #a78bfa;'>console.groq.com</a>
    </div>
    """, unsafe_allow_html=True)

# ─── Ana alan ────────────────────────────────────────────────────────────────
st.markdown("""
<div class='nexus-header'>
    <div class='nexus-title'>🤖 NexusAI</div>
    <div class='nexus-subtitle'>Groq ile güçlendirilmiş yapay zeka asistanı</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Mesajları göster
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class='msg-user'>{msg['content']}</div>
        <div class='msg-time' style='text-align:right; margin-right:4px;'>Sen</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-ai'>{msg['content']}</div>
        <div class='msg-time'>🤖 NexusAI</div>
        """, unsafe_allow_html=True)

# ─── Mesaj gönderme ───────────────────────────────────────────────────────────
st.divider()

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Mesaj",
            placeholder="Bir şeyler yaz...",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("➤ Gönder")

if submitted and user_input.strip():
    if not st.session_state.api_key:
        st.error("⚠️ Lütfen sol menüden Groq API key girin.")
    else:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({
            "role": "user",
            "content": user_input.strip(),
        })

        # AI yanıtı al
        with st.spinner("🤖 NexusAI yazıyor..."):
            try:
                client = Groq(api_key=st.session_state.api_key)
                response = client.chat.completions.create(
                    model=st.session_state.model,
                    messages=[
                        {"role": "system", "content": st.session_state.system_prompt}
                    ] + st.session_state.messages,
                    max_tokens=2048,
                    temperature=0.7,
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                })
            except Exception as e:
                err = str(e)
                if "401" in err or "api_key" in err.lower():
                    st.error("❌ Geçersiz API key.")
                elif "rate" in err.lower():
                    st.error("⚠️ Çok fazla istek. Biraz bekleyin.")
                else:
                    st.error(f"Hata: {err}")

        st.rerun()
