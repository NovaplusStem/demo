import streamlit as st
import json
import random
from chatbot_functies import chatbot_response

# ------------------------------------------------------------
# PAGINA-INSTELLINGEN
# ------------------------------------------------------------
st.set_page_config(
    page_title="Vraagstukken – Eerstegraadsvergelijkingen",
    page_icon="🧮",
    layout="centered"
)

# ------------------------------------------------------------
# HEADER MET LAYOUT
# ------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;">
        <img src="AP_logo_basis_rgb.jpg" width="220">
        <h1 style="margin-top:10px;">Vraagstukken-generator<br>Eerstegraadsvergelijkingen</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p style="text-align:center; color:#444;">
        Genereer realistische wiskunde‑vraagstukken in drie types,  
        vul je vergelijking in, controleer via meerkeuze  
        en geef een kort antwoord.
    </p>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SESSION STATE INITIALISATIE
# ------------------------------------------------------------
if "problem" not in st.session_state:
    st.session_state.problem = None
if "options" not in st.session_state:
    st.session_state.options = None
if "correct_index" not in st.session_state:
    st.session_state.correct_index = None

# ------------------------------------------------------------
# PROMPTBOUW
# ------------------------------------------------------------

EXAMPLE_BLOCK = """
VOORBEELDEN (NIET KOPIËREN, WÉL STIJL OVERNEMEN):

TYPE 1
"Het drievoud van een getal vermeerderd met 11/2 is gelijk aan de helft van dat getal vermeerderd met 4/3. Wat is dat getal?"

TYPE 2
"2 emmers bevatten samen 14 liter water. Emmer A bevat 5 liter water meer dan Emmer B. Hoeveel water bevat elke emmer?"

TYPE 3
"Ik heb 15,50 euro gespaard in mijn spaarpot waarin alleen stukken van 10 en 20 eurocent zitten.
Hoeveel stukken van elk heb ik, als je weet dat er 120 geldstukken in totaal in mijn spaarpot zitten?"
"""

def build_prompt(vraagstuk_type):
    type_uitleg = {
        "Type 1": "Eén onbekende. Eén vergelijking. Oplossing is een geheel getal.",
        "Type 2": "Twee onbekenden genoemd, maar door extra info reduceerbaar tot één onbekende.",
        "Type 3": "Twee onbekenden zonder info: leerling moet zelf kiezen welke x is (andere wordt geschreven in functie van x)."
    }[vraagstuk_type]

    return f"""
Je bent een Vlaamse leerkracht wiskunde. Genereer een nieuw, origineel vraagstuk
voor eerstegraadsvergelijkingen. Type: {vraagstuk_type}.

KENMERKEN:
- {type_uitleg}
- De vergelijking heeft een oplossing in één geheel getal.
- Gebruik natuurlijke contexten (prijzen, tijden, hoeveelheden,…)
- Tekst max. 90 woorden.
- Lever exact JSON terug in deze structuur:

{{
  "type": "{vraagstuk_type}",
  "problem_nl": "...",
  "equation_canonical": "...",
  "equation_options": [
      "...correcte vergelijking...",
      "...afleider 1...",
      "...afleider 2...",
      "...afleider 3..."
  ],
  "solution_integer": 0
}}

{EXAMPLE_BLOCK}

GEEN extra tekst buiten JSON.
"""


# ------------------------------------------------------------
# HELPER FUNCTIES
# ------------------------------------------------------------

def parse_json(raw_text):
    """Zoek JSON in het antwoord van de AI."""
    try:
        return json.loads(raw_text)
    except:
        try:
            start = raw_text.index("{")
            end = raw_text.rindex("}") + 1
            return json.loads(raw_text[start:end])
        except:
            return None

def shuffle_options(options):
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    nieuwe_lijst = [opt for _, opt in indexed]
    correct_idx = [i for i, (orig, _) in enumerate(indexed) if orig == 0][0]
    return nieuwe_lijst, correct_idx


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

st.sidebar.header("🛠️ Instellingen")
vraag_type = st.sidebar.radio(
    "Kies het type vraagstuk",
    ["Type 1", "Type 2", "Type 3", "Willekeurig"],
    index=3
)

# ------------------------------------------------------------
# KNOP OM TE GENEREREN
# ------------------------------------------------------------

st.divider()
col_gen, col_reset = st.columns([1,1])

with col_gen:
    if st.button("✨ Genereer nieuw vraagstuk", use_container_width=True):
        gekozen = random.choice(["Type 1", "Type 2", "Type 3"]) if vraag_type == "Willekeurig" else vraag_type
        prompt = build_prompt(gekozen)
        raw = chatbot_response(prompt)
        data = parse_json(raw)

        if data is None:
            st.error("Fout in AI‑antwoord. Probeer opnieuw.")
        else:
            st.session_state.problem = data
            opts, corr = shuffle_options(data["equation_options"])
            st.session_state.options = opts
            st.session_state.correct_index = corr
            st.success(f"Nieuw vraagstuk gegenereerd ({gekozen}).")

with col_reset:
    if st.button("🔄 Reset", use_container_width=True):
        st.session_state.problem = None
        st.session_state.options = None
        st.session_state.correct_index = None
        st.experimental_rerun()

st.divider()

# ------------------------------------------------------------
# HOOFDSCHERM
# ------------------------------------------------------------

if st.session_state.problem is None:
    st.info("Klik op **Genereer nieuw vraagstuk** om te starten.")
else:
    p = st.session_state.problem

    # Vraagstuk
    st.markdown(
        f"""
        <div style="background:#f6f6f9;padding:18px;border-radius:10px;margin-bottom:20px;">
            <h3 style="margin-top:0;">📘 Vraagstuk</h3>
            <p>{p["problem_nl"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Leerling vergelijking
    st.markdown("### ✍️ Schrijf jouw vergelijking")
    st.text_input("Typ jouw vergelijking (bijv. `2*x + 3 = 11`)", key="user_equation")

    # Meerkeuze
    st.markdown("### 📌 Controleer via meerkeuze")
    keuze = st.radio(
        "Welke vergelijking hoort bij het vraagstuk?",
        st.session_state.options,
        index=None
    )

    if st.button("🔍 Controleer vergelijking"):
        if keuze is None:
            st.warning("Kies eerst een vergelijking.")
        else:
            if st.session_state.options.index(keuze) == st.session_state.correct_index:
                st.success("✔️ Correct! Dit is de juiste vergelijking.")
            else:
                st.error("❌ Deze vergelijking klopt niet. Kijk nog eens goed naar de tekst.")

    # Oplossing (niet controleren, zoals je vroeg)
    st.markdown("### 🧮 Los je vergelijking op (optioneel)")
    st.text_area("Je stappen:", height=120)

    # Kort antwoord
    st.markdown("### 🎯 Kort antwoord (geheel getal)")
    antwoord = st.text_input("Jouw antwoord:")

    col_a, col_b = st.columns([1,1])
    with col_a:
        if st.button("⚖️ Controleer antwoord"):
            try:
                if int(antwoord) == int(p["solution_integer"]):
                    st.success("✔️ Correct!")
                else:
                    st.error("❌ Niet juist.")
            except:
                st.error("Geef een geheel getal in.")

    with col_b:
        if st.button("👀 Toon correcte oplossing"):
            st.info(f"Correcte waarde: **{p['solution_integer']}**")

    # Metadata
    with st.expander("ℹ️ Voor leerkrachten – details"):
        st.write("**Canonical vergelijking:**")
        st.code(p["equation_canonical"])
        st.write("**Meerkeuze (oorspronkelijke volgorde):**")
        st.code("\n".join(p["equation_options"]))