import streamlit as st
from chatbot_functies import chatbot_response


col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("AP_logo_basis_rgb.jpg", width=300)
st.title("🤖 Mijn AI Assistent 🤖")
form = st.form(key="user_settings")
with form:
    AI_concept = st.text_input("Voer het AI-concept in dat je wilt leren:", key = "AI_concept")
    role = st.selectbox("Voor welk publiek wil je het uitgelegd hebben?",
                          ("Expert",
                           "Leek", "12-jarig kind"),)
    generate_button = form.form_submit_button("Leg AI-concept uit")
    if generate_button:
        with st.spinner('Even geduld...'):
            PROMPT = f"""Leg het AI-concept {AI_concept} bondig uit aan iemand met de ervaring van een {role} op het gebied van kunstmatige intelligentie.
            Geef geen antwoord als het concept niet gerelateerd is aan AI. Antwoord in het Nederlands."""
            response = chatbot_response(PROMPT)
        st.write(response)
