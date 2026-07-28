import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="NexusAI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "model" not in st.session_state:
    st.session_state.model = "llama-3.1-8b-instant"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "Sen yardımcı bir yapay zeka asistanısın. Türkçe konuşuyorsun."
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0f0f1a"

# ─── Sidebar ─────────────────────────────────────────────────────────────────
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
        "meta-llama/llama-4-maverick-17b-128e-instruct",
            "gemma2-9b-it",
            "mixtral-8x7b-32768",
        ],
        index=0,
        help="Fotoğraf göndermek için llama-4-maverick modelini seçin",
    )
    st.session_state.model = model

    st.divider()
    st.markdown("**🎨 Arka Plan Rengi**")

    renkler = {
        "Koyu (Varsayılan)": "#0f0f1a",
        "Mor": "#1a0a2e",
        "Lacivert": "#0a1628",
        "Koyu Yeşil": "#0a1f0d",
        "Koyu Kırmızı": "#1f0a0a",
        "Antrasit": "#111118",
    }

    secilen = st.selectbox("Tema", options=list(renkler.keys()), index=0)
    st.session_state.bg_color = renkler[secilen]

    st.divider()

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

    st.markdown(
        "<div style='color:#666;font-size:0.8rem;margin-top:20px;'>Ücretsiz API key:<br>"
        "<a href='https://console.groq.com' target='_blank' style='color:#a78bfa;'>console.groq.com</a></div>",
        unsafe_allow_html=True,
    )

# ─── CSS ─────────────────────────────────────────────────────────────────────
bg = st.session_state.bg_color
st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; }}
    [data-testid="stSidebar"] {{ background-color: #13131f !important; }}
    .nexus-title {{ font-size: 2.2rem; font-weight: 800; color: #a78bfa; letter-spacing: 2px; text-align: center; }}
    .nexus-subtitle {{ font-size: 0.95rem; color: #888; margin-top: 4px; text-align: center; margin-bottom: 10px; }}
    .msg-user {{
        background: #3a3a5c;
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin: 8px 0 8px 15%;
        font-size: 1rem;
        line-height: 1.5;
    }}
    .msg-ai {{
        background: #1e1e2e;
        color: #e0e0e0;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin: 8px 15% 8px 0;
        font-size: 1rem;
        line-height: 1.5;
        border-left: 3px solid #a78bfa;
    }}
    .msg-time {{ font-size: 0.75rem; color: #666; margin-top: 4px; }}
    .stTextInput input, .stTextArea textarea {{
        background-color: #1e1e2e !important;
        color: white !important;
        border: 1px solid #3a3a5c !important;
        border-radius: 10px !important;
    }}
    .stButton button {{
        background-color: #7c3aed !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        width: 100%;
    }}
    .stButton button:hover {{ background-color: #6d28d9 !important; }}
    hr {{ border-color: #2a2a3e; }}
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {bg}; }}
    ::-webkit-scrollbar-thumb {{ background: #3a3a5c; border-radius: 3px; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    [data-testid="stSidebar"] input {{ color: white !important; background-color: #1e1e2e !important; }}
    [data-testid="stSidebar"] input::placeholder {{ color: #aaaaaa !important; }}
    [data-testid="stSidebar"] textarea {{ color: white !important; background-color: #1e1e2e !important; }}
    input::placeholder {{ color: #aaaaaa !important; }}
    .stTextInput input {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# ─── Ana alan ────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='nexus-title'>🤖 NexusAI</div>"
    "<div class='nexus-subtitle'>Groq ile güçlendirilmiş yapay zeka asistanı</div>",
    unsafe_allow_html=True,
)
st.divider()

# Mesajları göster
for msg in st.session_state.messages:
    if msg["role"] == "user":
        content = msg["content"]
        if isinstance(content, list):
            # Fotoğraflı mesaj
            text_part = next((c["text"] for c in content if c["type"] == "text"), "")
            img_part = next((c for c in content if c["type"] == "image_url"), None)
            st.markdown(
                f"<div class='msg-user'>{text_part}</div>"
                "<div class='msg-time' style='text-align:right;'>Sen</div>",
                unsafe_allow_html=True,
            )
            if img_part:
                img_data = img_part["image_url"]["url"].split(",")[1]
                img_bytes = base64.b64decode(img_data)
                st.image(Image.open(io.BytesIO(img_bytes)), width=200)
        else:
            st.markdown(
                f"<div class='msg-user'>{content}</div>"
                "<div class='msg-time' style='text-align:right;'>Sen</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f"<div class='msg-ai'>{msg['content']}</div>"
            "<div class='msg-time'>🤖 NexusAI</div>",
            unsafe_allow_html=True,
        )

st.divider()

# ─── Mesaj gönderme ───────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "� Fotoğraf ekle (isteğe bağlı)",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="visible",
)

if uploaded_file:
    st.image(uploaded_file, width=200, caption="Yüklenecek fotoğraf")

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

if submitted and (user_input.strip() or uploaded_file):
    if not st.session_state.api_key:
        st.error("⚠️ Lütfen sol menüden Groq API key girin.")
    else:
        text = user_input.strip() or "Bu fotoğrafı analiz et."

        # Fotoğraf varsa vision modeline geç
        if uploaded_file:
            img_bytes = uploaded_file.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            ext = uploaded_file.type
            content = [
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": f"data:{ext};base64,{img_b64}"}},
            ]
            vision_model = "qwen/qwen3.6-27b"
        else:
            content = text
            vision_model = st.session_state.model

        st.session_state.messages.append({"role": "user", "content": content})

        with st.spinner("🤖 NexusAI yazıyor..."):
            try:
                client = Groq(api_key=st.session_state.api_key)
                # Vision için sadece son mesajı gönder (geçmiş fotoğrafları atla)
                api_messages = [{"role": "system", "content": st.session_state.system_prompt}]
                for m in st.session_state.messages:
                    if isinstance(m["content"], list):
                        api_messages.append({"role": m["role"], "content": m["content"]})
                    else:
                        api_messages.append({"role": m["role"], "content": m["content"]})

                response = client.chat.completions.create(
                    model=vision_model,
                    messages=api_messages,
                    max_tokens=2048,
                    temperature=0.7,
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                err = str(e)
                if "401" in err or "api_key" in err.lower():
                    st.error("❌ Geçersiz API key.")
                elif "rate" in err.lower():
                    st.error("⚠️ Çok fazla istek. Biraz bekleyin.")
                else:
                    st.error(f"Hata: {err}")
        st.rerun()
