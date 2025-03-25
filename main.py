import streamlit as st
from openai import OpenAI

# Sayfa yapısı
st.set_page_config(layout="wide")

# API Key giriş popup'ı
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

if not st.session_state["api_key"]:
    with st.form("API Form"):
        st.subheader("🔑 OpenAI API Key")
        api_input = st.text_input("Lütfen OpenAI API anahtarınızı girin:", type="password")
        submitted = st.form_submit_button("Kaydet")
        if submitted and api_input:
            st.session_state["api_key"] = api_input
            st.rerun()

# API Key varsa devam
if st.session_state["api_key"]:
    client = OpenAI(api_key=st.session_state["api_key"])

    from gpt_education_details_full import education_details
    from gpt_career_details_final import career_details

    education_topics = list(education_details.keys())
    career_experiences = list(career_details.keys())

    st.markdown("""
        <style>
        .block-container { padding-left: 3rem !important; padding-right: 3rem !important; }
        .stColumn { padding: 1rem !important; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.subheader("🎓 Aldığınız Eğitimler")
        selected_education = [t for t in education_topics if st.checkbox(t, key=f"edu_{t}")]

    with col2:
        st.subheader("💼 İş Tecrübeleriniz")
        selected_career = [j for j in career_experiences if st.checkbox(j, key=f"car_{j}")]

    with col3:
        st.markdown("###")

        style = st.selectbox("Soru tarzını seçin:", ["Düşündürücü", "Teknik", "Meraklı", "Esprili", "Minimal"])

        style_prompts = {
            "Düşündürücü": (
                "Eğitim geçmişi ve kariyer deneyimlerini ilişkilendirerek, düşünmeye sevk eden ama sade bir soru üret. "
                "Örneğin: 'Simülasyon Teknikleri eğitimin, hasar analizi yaptığın dönemde kararlarını nasıl şekillendirdi?' gibi."
            ),
            "Teknik": (
                "Teknik içeriği olan ama sade anlatımlı, uzmanlık hissi veren ve eğitimle iş tecrübesini bağlayan bir soru üret."
            ),
            "Meraklı": "Soru, samimi ama araştırmacı bir bakış açısıyla gelsin. Yeni bir şey öğrenmek isteyen bir öğrenci gibi yaz.",
            "Esprili": "Soru biraz mizahi, rahat, eğlenceli ama hâlâ bilgiye odaklı olsun.",
            "Minimal": "Kısa, doğrudan, sade bir soru üret. 1 cümleyi geçmesin."
        }

        if st.button("Ask me anything?"):
            if selected_education and selected_career:
                edu_text = ", ".join(selected_education)
                car_text = ", ".join(selected_career)
                user_prompt = (
                    f"Kullanıcı {edu_text} alanlarında eğitim almıştır ve "
                    f"{car_text} görevlerinde bulunmuştur. "
                    f"{style_prompts[style]} "
                    "Sadece soru üret. Giriş, açıklama, bağlam veya yönlendirme cümlesi yazma. "
                    "Yanıtın ilk kelimesi doğrudan sorunun içeriğiyle başlasın. "
                    "‘İşte sana bir soru’, ‘Tabii ki’ gibi ifadeler kullanma."
                )

                with st.spinner("GPT düşünüyor..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.4,
                        max_tokens=200
                    )
                    st.session_state["last_question"] = response.choices[0].message.content.strip()
                    st.session_state.setdefault("mourinho_answer", "")
                    st.session_state.setdefault("terim_answer", "")

        if "last_question" in st.session_state:
            st.success("Soru oluşturuldu:")
            st.markdown(f"""
<div style="background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
            border-radius: 8px; padding: 1rem; font-family: 'Courier New', monospace;
            font-size: 0.95rem; width: 100%; height: auto; overflow-x: auto;
            white-space: pre-wrap; word-break: break-word;">
{st.session_state["last_question"]}
</div>
""", unsafe_allow_html=True)

    with col4:
        st.subheader("🛠️ Planlı Alan")

        if "last_question" in st.session_state:
            col_m, col_f = st.columns(2)
            with col_m:
                if st.button("Mourinho'dan yardım iste"):
                    with st.spinner("Mourinho düşünüyor..."):
                        result = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are Jose Mourinho. You are clever, direct and slightly arrogant, but always insightful and respectful. Answer briefly."},
                                {"role": "user", "content": st.session_state["last_question"]}
                            ],
                            temperature=0.5,
                            max_tokens=150
                        )
                        st.session_state["mourinho_answer"] = result.choices[0].message.content.strip()

            with col_f:
                if st.button("Fatih Terim'den yardım iste"):
                    with st.spinner("Fatih Hoca hazırlanıyor..."):
                        result = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are Fatih Terim. You are passionate, motivational, assertive, and respectful. You answer with strong belief and confidence, but keep it concise."},
                                {"role": "user", "content": st.session_state["last_question"]}
                            ],
                            temperature=0.6,
                            max_tokens=150
                        )
                        st.session_state["terim_answer"] = result.choices[0].message.content.strip()

        if st.session_state.get("mourinho_answer"):
            st.markdown(f"""
<div style="background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
            border-radius: 8px; padding: 1rem; font-family: 'Courier New', monospace;
            font-size: 0.95rem; width: 100%; height: auto; overflow-x: auto;
            white-space: pre-wrap; word-break: break-word;">
<b>Mourinho'dan Cevap:</b>

{st.session_state["mourinho_answer"]}
</div>
""", unsafe_allow_html=True)

        if st.session_state.get("terim_answer"):
            st.markdown(f"""
<div style="background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
            border-radius: 8px; padding: 1rem; font-family: 'Courier New', monospace;
            font-size: 0.95rem; width: 100%; height: auto; overflow-x: auto;
            white-space: pre-wrap; word-break: break-word;">
<b>Fatih Terim'den Cevap:</b>

{st.session_state["terim_answer"]}
</div>
""", unsafe_allow_html=True)

        else:
            st.info("Henüz oluşturulmuş bir soru yok. Önce 'Ask me anything?' butonuna tıklayın.")
