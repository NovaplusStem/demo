# app.py
import os
import json
import random
import streamlit as st
from chatbot_functies import chatbot_response

# ------------------------- Pagina & Thema -------------------------
st.set_page_config(
    page_title="Vraagstukken – Eerstegraadsvergelijkingen",
    page_icon="🧮",
    layout="centered",
)

# Custom CSS (strak, professioneel; geen AI-gevoel)
st.markdown(
    """
    <style>
    :root {
        --brand:#274C77;
        --accent:#E7ECEF;
        --ok:#2E7D32;
        --warn:#D32F2F;
    }
    .main > div { padding-top: 1rem; }
    .app-header {
        background: linear-gradient(90deg, #274C77 0%, #43658B 100%);
        color: #fff; border-radius: 12px; padding: 18px 20px; text-align:center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    .app-card {
        background: #fff; border: 1px solid #e8e8e8; border-radius: 12px; padding: 16px 18px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04); margin-bottom: 18px;
    }
    .kicker { font-size: 0.95rem; color:#e6f3ff; opacity:.95; letter-spacing:.4px; margin-bottom:6px; }
    .app-title { margin:0; font-size: 1.0rem; font-weight: 700; letter-spacing:.5px; }
    .muted { color:#606770; }
    .option-pill { background:#f6f8fb; border:1px solid #e6eaf1; padding:6px 10px; border-radius:8px; display:inline-block; margin:4px 6px 0 0; color:#2c3a4b; }
    .context-chip { background:#274C77; color:#fff; padding:4px 10px; border-radius:999px; display:inline-block; font-size:0.9rem; }
    .metadata { background:#f7fafc; border:1px dashed #d9e2ec; padding:12px; border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------- Header -------------------------
logo_path = "AP_logo_basis_rgb.jpg"
with st.container():
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    cols = st.columns([1, 3, 1])
    with cols[0]:
        if os.path.exists(logo_path):
            st.image(logo_path, width=90)
    with cols[1]:
        st.markdown('<div class="kicker">Wiskunde • Lineaire vergelijkingen</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="app-title">Vraagstukken‑generator</h1>', unsafe_allow_html=True)
        st.markdown('<div class="muted">Genereer realistische verhalen, modelleer de juiste vergelijking en controleer je antwoord.</div>', unsafe_allow_html=True)
    with cols[2]:
        pass
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- Session state -------------------------
if "problem" not in st.session_state:
    st.session_state.problem = None
if "options" not in st.session_state:
    st.session_state.options = None
if "correct_index" not in st.session_state:
    st.session_state.correct_index = None
if "last_context" not in st.session_state:
    st.session_state.last_context = None  # voorkom herhaling bij Willekeurig
if "recent_contexts" not in st.session_state:
    st.session_state.recent_contexts = []  # korte historie om afwisseling te garanderen

# ------------------------- Voorbeeld-ankers -------------------------
EXAMPLE_BLOCK = """
VOORBEELDEN VAN STIJL (NIET KOPIËREN, WÉL STIJL/TOON OVERNEMEN):

TYPE 1 (1 onbekende):
"Het drievoud van een getal vermeerderd met 11/2 is gelijk aan de helft van dat getal vermeerderd met 4/3. Wat is dat getal?"

TYPE 2 (2 onbekenden genoemd, uiteindelijk 1 onbekende door extra info):
"2 emmers bevatten samen 14 liter water. Emmer A bevat 5 liter water meer dan Emmer B. Hoeveel water bevat elke emmer?"

TYPE 3 (2 onbekenden zonder directe info; kies zelf welke x is, de andere schrijf je uit in functie van x):
"Ik heb 15,50 euro gespaard in mijn spaarpot waarin alleen stukken van 10 en 20 eurocent zitten.
Hoeveel stukken van elk heb ik, als je weet dat er 120 geldstukken in totaal in mijn spaarpot zitten?"
"""

# Contextcategorieën met brede variatie (bakkerij vermijden)
CONTEXT_CATEGORIES = [
    "Sport", "Muziek", "Natuur", "School", "Reizen", "Technologie", "Gezin",
    "Dieren", "Spel/Games", "Tuinieren", "Kunst/Cultuur", "Wetenschap",
    "Vervoer/Transport", "Financiën/Geld", "Bouwen/Klus", "Gezondheid/Fitness",
    "Evenementen", "Voeding (geen bakkerij)", "Restaurant (geen bakkerij)"
]
VERBODEN_WOORDEN_DEFAULT = ["bakkerij", "bakker", "brood", "koek", "koeken", "koffiekoek", "pistolet", "sandwich"]

# ------------------------- Promptbouw -------------------------
def build_generation_prompt(problem_type: str,
                            context_category: str,
                            forbidden_terms: list[str],
                            max_abs_val: int) -> str:
    type_expl = {
        "Type 1": "Formuleer een realistisch verhaaltje waarbij je één onbekende (x) nodig hebt. Eén eerstegraadsvergelijking, één gehele oplossing.",
        "Type 2": "Noem twee onbekenden, maar geef informatie zodat je in feite met één onbekende x kunt modelleren (de tweede is afleidbaar/irrelevant). Eindig met één eerstegraadsvergelijking en een geheel getal als oplossing.",
        "Type 3": "Noem twee onbekenden zonder directe info; de leerling moet een keuze maken voor x en de andere onbekende uitdrukken in functie van x. Het model reduceert tot één eerstegraadsvergelijking met een geheel getal als oplossing."
    }[problem_type]

    # Contextregels voor variatie
    forbidden_block = ", ".join(sorted(set(t.lower() for t in forbidden_terms)))
    last_context = st.session_state.last_context
    recent_line = ""
    if last_context:
        recent_line = f"- Gebruik **niet** opnieuw de vorige categorie (“{last_context}”). Kies bewust voor variatie.\n"

    prompt = f"""
Je bent een ervaren leerkracht wiskunde (Vlaanderen). Genereer **één nieuw** en **origineel** vraagstuk over **eerstegraadsvergelijkingen**.

TYPE:
- {type_expl}

CONTEXT:
- **Gebruik verplicht deze contextcategorie:** {context_category}.
{recent_line}- Vermijd **herhaling** van eerdere scenario's; kies telkens een andere concrete insteek binnen de categorie.
- De volgende termen en domeinen zijn **verboden** (niet noemen, niet suggereren): {forbidden_block}.

EISEN VOOR HET VRAAGSTUK:
- Tekst max. 90 woorden, helder en eenduidig Nederlands.
- Coëfficiënten en constanten kies je uit het bereik [-{max_abs_val}, {max_abs_val}] waar logisch (bv. geen negatieve aantallen voor echte stuks).
- Gebruik **x** als modelvariabele (vermeld x niet expliciet in de tekst, maar wel in de vergelijking).
- De **oplossing** is **exact één geheel getal** (solution_integer).
- Bouw **3 afleider-vergelijkingen** met typische fouten (teken, constante, factor) zodat **exact 1** optie correct is.

UITVOER (STRICTE JSON, GEEN extra tekst):
{{
  "type": "{problem_type}",
  "context_category": "{context_category}",
  "problem_nl": "… korte tekst …",
  "equation_canonical": "… enkele vergelijking in x, gebruik * voor vermenigvuldiging, precies één '=' …",
  "equation_options": [
    "… correcte vergelijking (identiek aan equation_canonical) …",
    "… afleider 1 …",
    "… afleider 2 …",
    "… afleider 3 …"
  ],
  "solution_integer": 0
}}

AANDACHT:
- Controleer intern dat de vergelijking consistent is met de tekst en een **gehele** oplossing oplevert.
- Geef **uitsluitend** de JSON terug.

{EXAMPLE_BLOCK}
"""
    return prompt.strip()

# ------------------------- Hulpfuncties -------------------------
def parse_llm_json(raw: str) -> dict | None:
    """Probeer JSON te parsen uit het LLM-antwoord; met fallback op substring."""
    try:
        return json.loads(raw)
    except Exception:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return None

def shuffle_options(options: list[str]) -> tuple[list[str], int]:
    """Shuffelt opties en retourneert (nieuwe_lijst, index_correcte). Correct is index 0 in de origine."""
    indexed = list(enumerate(options))
    random.shuffle(indexed)
    new_opts = [opt for _, opt in indexed]
    correct_idx = next(i for i, (orig, _) in enumerate(indexed) if orig == 0)
    return new_opts, correct_idx

def choose_context(user_choice: str) -> str:
    """Kies context op basis van gebruiker; bij Willekeurig vermijd de vorige categorie."""
    if user_choice != "Willekeurig":
        return user_choice
    pool = [c for c in CONTEXT_CATEGORIES if c != st.session_state.last_context]
    if not pool:
        pool = CONTEXT_CATEGORIES[:]  # fallback
    return random.choice(pool)

# ------------------------- Sidebar -------------------------
st.sidebar.header("🎛️ Instellingen")

vraag_type = st.sidebar.radio(
    "Type vraagstuk",
    ["Type 1", "Type 2", "Type 3", "Willekeurig"],
    index=3
)

context_keuze = st.sidebar.selectbox(
    "Contextcategorie",
    ["Willekeurig"] + CONTEXT_CATEGORIES,
    index=0
)

moeilijkheid = st.sidebar.slider(
    "Maximale grootte coëfficiënten/constanten",
    min_value=5, max_value=40, value=15, step=1,
    help="Stuurt de grootte van getallen in de gegenereerde vergelijking."
)

extra_verboden_input = st.sidebar.text_input(
    "Extra verboden woorden (komma‑gescheiden)",
    help="Bijv.: voetbal, treinkaartje"
)

# Combineer verboden woorden
verboden_woorden = VERBODEN_WOORDEN_DEFAULT[:]
if extra_verboden_input.strip():
    extra_terms = [t.strip().lower() for t in extra_verboden_input.split(",") if t.strip()]
    verboden_woorden.extend(extra_terms)

# ------------------------- Generator knoppen -------------------------
top_cols = st.columns([1, 1, 1])
with top_cols[0]:
    gen_btn = st.button("✨ Genereer nieuw vraagstuk", use_container_width=True)
with top_cols[1]:
    reset_btn = st.button("🔄 Reset", use_container_width=True)
with top_cols[2]:
    show_meta_toggle = st.toggle("ℹ️ Toon leerkrachtinfo", value=False)

if reset_btn:
    st.session_state.problem = None
    st.session_state.options = None
    st.session_state.correct_index = None
    st.session_state.last_context = None
    st.session_state.recent_contexts = []
    st.experimental_rerun()

# ------------------------- Genereren -------------------------
if gen_btn:
    chosen_type = random.choice(["Type 1", "Type 2", "Type 3"]) if vraag_type == "Willekeurig" else vraag_type
    chosen_context = choose_context(context_keuze)

    prompt = build_generation_prompt(
        problem_type=chosen_type,
        context_category=chosen_context,
        forbidden_terms=verboden_woorden,
        max_abs_val=moeilijkheid
    )

    with st.spinner("Even geduld… een nieuw verhaal wordt bedacht…"):
        raw = chatbot_response(prompt)

    data = parse_llm_json(raw)
    if not data:
        st.error("Kon de AI‑uitvoer niet lezen. Probeer opnieuw.")
    else:
        # Basale validatie/normalisatie
        if "equation_options" not in data or not isinstance(data["equation_options"], list):
            st.error("AI gaf geen geldige meerkeuze‑opties terug. Probeer opnieuw.")
        else:
            # Zorg dat eerste optie == canonical
            if "equation_canonical" in data and data["equation_options"]:
                if data["equation_options"][0].replace(" ", "") != data["equation_canonical"].replace(" ", ""):
                    data["equation_options"][0] = data["equation_canonical"]

            st.session_state.problem = data
            st.session_state.options, st.session_state.correct_index = shuffle_options(data["equation_options"])

            # Contextrotatie bijhouden (voor variatie)
            ctx = data.get("context_category", chosen_context)
            st.session_state.last_context = ctx
            st.session_state.recent_contexts.append(ctx)
            st.session_state.recent_contexts = st.session_state.recent_contexts[-4:]  # kort geheugen

            st.success(f"Nieuw vraagstuk gegenereerd ({data.get('type', chosen_type)} – {ctx}).")

# ------------------------- Hoofdscherm / Interactie -------------------------
if st.session_state.problem is None:
    st.markdown(
        """
        <div class="app-card">
          <b>Tip:</b> Kies links een <em>Type</em> en een <em>Contextcategorie</em>, klik daarna op
          <b>✨ Genereer nieuw vraagstuk</b>.
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    p = st.session_state.problem
    used_ctx = p.get("context_category", st.session_state.last_context or "—")

    # Vraagstuk
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="context-chip">Context: {used_ctx}</div>', unsafe_allow_html=True)
    st.markdown("### 📘 Vraagstuk")
    st.write(p.get("problem_nl", "").strip())
    st.markdown('</div>', unsafe_allow_html=True)

    # Jouw vergelijking
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown("### ✍️ Jouw vergelijking")
    user_eq = st.text_input("Schrijf jouw vergelijking (bijv. `2*x + 3 = 11`).", key="user_eq")
    st.markdown("**Controleer via meerkeuze** — welke vergelijking hoort bij het vraagstuk?")
    selected = st.radio(
        label="Kies de juiste vergelijking:",
        options=st.session_state.options,
        index=None,
        format_func=lambda s: s.replace("*", "·")
    )
    check_cols = st.columns([1, 2])
    with check_cols[0]:
        if st.button("✅ Controleer vergelijking"):
            if selected is None:
                st.warning("Selecteer eerst een optie.")
            else:
                if st.session_state.options.index(selected) == st.session_state.correct_index:
                    st.success("Correct! Je koos de juiste vergelijking.")
                else:
                    st.error("Niet juist. Kijk nog eens goed naar de gegevens in de tekst.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Oplossing (vrij veld)
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown("### 🧮 Los je vergelijking op (stappen, niet automatisch gecontroleerd)")
    st.text_area("Toon hier je redenering/stappen:", height=120, key="workings")
    st.markdown('</div>', unsafe_allow_html=True)

    # Kort antwoord (geheel getal)
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Kort antwoord (geheel getal)")
    ans = st.text_input("Jouw eindantwoord:", key="short_answer", placeholder="bv. 7")
    ans_cols = st.columns([1, 1])
    with ans_cols[0]:
        if st.button("🔎 Controleer antwoord"):
            if ans.strip() == "":
                st.warning("Vul eerst een getal in.")
            else:
                try:
                    user_val = int(ans.strip())
                    correct_val = int(p.get("solution_integer", 0))
                    if user_val == correct_val:
                        st.success("Top! Je korte antwoord is correct.")
                    else:
                        st.error("Niet juist. Probeer opnieuw of toon de correcte waarde.")
                except ValueError:
                    st.error("Geef een **geheel getal** in (zonder komma).")
    with ans_cols[1]:
        if st.button("👀 Toon correcte waarde"):
            st.info(f"**Correcte waarde:** {p.get('solution_integer', '—')}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Leerkrachtinfo
    if show_meta_toggle:
        with st.expander("ℹ️ Voor de leerkracht – metadata"):
            st.markdown('<div class="metadata">', unsafe_allow_html=True)
            st.markdown("**Canonical vergelijking:**")
            st.code(p.get("equation_canonical", ""), language="text")
            st.markdown("**Meerkeuze (oorspronkelijke volgorde):**")
            st.code("\n".join(p.get("equation_options", [])), language="text")
            st.markdown("**Volledige JSON:**")
            st.code(json.dumps(p, indent=2, ensure_ascii=False), language="json")
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------- Footer -------------------------
st.caption("💡 Contexten roteren automatisch en 'bakkerij' is uitgesloten om herhaling te vermijden. Pas dit aan in de sidebar indien nodig.")