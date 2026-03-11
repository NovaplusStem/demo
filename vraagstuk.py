import streamlit as st
import random

# ==============================
# Hulpfuncties
# ==============================
def normalize_formula(s: str) -> str:
    """Normaliseer een formule-string om eenvoudige controles mogelijk te maken."""
    if s is None:
        return ""
    n = s.strip().lower()
    # vervang veelgebruikte tekens
    n = n.replace(" ", "")
    n = n.replace("×", "*").replace("·", "*")
    n = n.replace(",", ".")
    # haal "v=" of "volume=" weg
    if n.startswith("v="):
        n = n[2:]
    if n.startswith("volume="):
        n = n[7:]
    return n

def is_formula_correct(shape: str, formula: str) -> bool:
    """Controleer of de ingevoerde formule correct is voor de gevraagde vorm."""
    n = normalize_formula(formula)

    if shape == "kubus":
        # Toegestaan: z^3, z*z*z, z×z×z
        if n in {"z^3", "z*z*z"}:
            return True
        # Ook accepteren als ze sterretjes weglaten (zzz)
        if n.replace("*", "") == "zzz":
            return True
        return False

    if shape == "balk":
        # Toegestaan: l*b*h in eender welke volgorde, met *, ×, of ·
        # Verwijder * en controleer of de letters precies l, b, h bevatten.
        raw = n.replace("*", "")
        # Soms schrijven leerlingen hoofdletters, maar we hebben al lower() gedaan.
        letters = sorted(list(raw))
        return letters == sorted(list("lbh"))

    if shape == "prisma":
        # Recht prisma met driehoekige doorsnede.
        # Toegestaan: (b*h/2)*l, 0.5*b*h*l, (b*h*l)/2, (1/2)*b*h*l
        # We eisen: bevat b, h, l én factor 1/2 (via '/2' of '0.5' of '1/2').
        has_b = "b" in n
        has_h = "h" in n
        # let op: lengte is L, maar na lower() is dat 'l'
        has_L = "l" in n
        has_half = ("/2" in n) or ("0.5" in n) or ("1/2" in n)
        return has_b and has_h and has_L and has_half

    return False


def gen_kubus_problem():
    # Mooie, kleine getallen
    z = random.randint(2, 12)  # zijde (cm)
    volume = z ** 3  # cm³
    # kindvriendelijke contexten
    scenarios = [
        f"Je hebt een **kubusvormig doosje** voor knikkers. Elke zijde is **{z} cm** lang.",
        f"Een **dobbelsteen** is bijna een perfecte kubus. Stel dat elke ribbe **{z} cm** is.",
        f"Een **vierkante pakdoos** heeft gelijke zijden van **{z} cm**."
    ]
    tekst = random.choice(scenarios)
    gegevens = f"- Zijde (z) = **{z} cm**"
    hint_vars = "Gebruik **z** voor de zijde."
    return {
        "shape": "kubus",
        "text": tekst,
        "data_text": gegevens,
        "vars_hint": hint_vars,
        "volume": int(round(volume)),
        "units": "cm³",
        "dimensions": {"z": z},
        "expected_formula": "V = z³"
    }


def gen_balk_problem():
    l = random.randint(6, 20)   # lengte (cm)
    b = random.randint(4, 15)   # breedte (cm)
    h = random.randint(3, 12)   # hoogte (cm)
    volume = l * b * h
    scenarios = [
        f"Je wil een **pennenbakje** in de vorm van een balk maken. Het is **{l} cm** lang, **{b} cm** breed en **{h} cm** hoog.",
        f"Een **boekendoos** (balk) is **{l} cm** lang, **{b} cm** breed en **{h} cm** hoog.",
        f"Een **lego‑doos** heeft de vorm van een balk: **{l} × {b} × {h} cm**."
    ]
    tekst = random.choice(scenarios)
    gegevens = f"- Lengte (l) = **{l} cm**\n- Breedte (b) = **{b} cm**\n- Hoogte (h) = **{h} cm**"
    hint_vars = "Gebruik **l** (lengte), **b** (breedte) en **h** (hoogte)."
    return {
        "shape": "balk",
        "text": tekst,
        "data_text": gegevens,
        "vars_hint": hint_vars,
        "volume": int(round(volume)),
        "units": "cm³",
        "dimensions": {"l": l, "b": b, "h": h},
        "expected_formula": "V = l × b × h"
    }


def gen_prisma_problem():
    # Triangulaire doorsnede: oppervlak = (b*h)/2, volume = A * L
    # Zorg dat b*h even is, zodat volume een geheel getal blijft.
    b = random.choice([x for x in range(4, 21)])           # cm
    h = random.choice([x for x in range(4, 17)])           # cm
    if (b * h) % 2 == 1:  # maak product even
        h += 1
    L = random.randint(6, 20)                              # lengte prisma (cm)
    A = (b * h) / 2
    volume = int(round(A * L))
    scenarios = [
        f"Een **dakgoot‑model** heeft een **driehoekige doorsnede**. De driehoek heeft basis **{b} cm** en hoogte **{h} cm**. "
        f"De goot is **{L} cm** lang.",
        f"Je knutselt een **tentje** als recht prisma: de **driehoekige voorkant** heeft basis **{b} cm** en hoogte **{h} cm**. "
        f"De tent is **{L} cm** lang.",
        f"Een **chocoladevorm** is een recht prisma met **driehoekige doorsnede**: basis **{b} cm**, hoogte **{h} cm**, lengte **{L} cm**."
    ]
    tekst = random.choice(scenarios)
    gegevens = (
        f"- Basis driehoek (b) = **{b} cm**\n"
        f"- Hoogte driehoek (h) = **{h} cm**\n"
        f"- Lengte prisma (L) = **{L} cm**"
    )
    hint_vars = "Gebruik **b** (basis van de driehoek), **h** (hoogte van de driehoek) en **L** (lengte van het prisma)."
    return {
        "shape": "prisma",
        "text": tekst,
        "data_text": gegevens,
        "vars_hint": hint_vars,
        "volume": volume,
        "units": "cm³",
        "dimensions": {"b": b, "h": h, "L": L},
        "expected_formula": "V = (b × h / 2) × L"
    }


def generate_problem(fixed_shape=None):
    """Kies willekeurig of gebruik een vaste vorm."""
    if fixed_shape == "kubus":
        return gen_kubus_problem()
    if fixed_shape == "balk":
        return gen_balk_problem()
    if fixed_shape == "prisma":
        return gen_prisma_problem()
    # Willekeurig
    return random.choice([gen_kubus_problem, gen_balk_problem, gen_prisma_problem])()


def reset_state(new_shape=None):
    st.session_state.problem = generate_problem(new_shape)
    st.session_state.formula_ok = False
    st.session_state.formula_input = ""
    st.session_state.answer_input = 0
    st.session_state.feedback_formula = ""
    st.session_state.feedback_answer = ""


# ==============================
# UI
# ==============================
st.set_page_config(page_title="Inhoud berekenen – 6e leerjaar", page_icon="📦", layout="centered")
st.title("📦 Inhoud (volume) berekenen – oefenmodule")

st.markdown(
    "Deze oefenmodule maakt **steeds nieuwe situaties** over de inhoud (volume) van een **kubus**, **balk** of **recht prisma**. "
    "Eerst controleer je de **formule**, daarna geef je het **antwoord in cm³** (tot op de eenheid)."
)

# Sidebar: keuze om een vorm vast te zetten (voor differentiatie)
st.sidebar.header("Opties (voor leerkracht)")
mode = st.sidebar.radio("Vormkeuze", ["Willekeurig", "Vast"])
fixed_shape = None
if mode == "Vast":
    fixed_shape = st.sidebar.selectbox("Kies de vorm", ["kubus", "balk", "prisma"])

# Initialiseer state
if "problem" not in st.session_state:
    reset_state(fixed_shape)

# Knoppen bovenaan
colA, colB = st.columns([1, 1])
with colA:
    if st.button("🔄 Nieuwe situatie", use_container_width=True):
        reset_state(fixed_shape)

with colB:
    with st.popover("ℹ️ Hints"):
        st.markdown(
            """
            **Formules:**
            - Kubus: `V = z³`
            - Balk: `V = l × b × h`
            - Recht prisma (driehoekig): `V = (b × h / 2) × L`

            **Eenheden:** alle afmetingen in **cm** → **volume in cm³**.
            """
        )

problem = st.session_state.problem

# Situatie
st.subheader("Situatie")
st.write(problem["text"])
st.markdown(problem["data_text"])
st.caption(problem["vars_hint"])

# Stap 1: formule ingeven
st.subheader("Stap 1 — Schrijf de formule")
st.write("Schrijf de **juiste formule** met de letters zoals hierboven.")
formula = st.text_input(
    "Formule (bv. V = l × b × h)",
    key="formula_input",
    placeholder=problem["expected_formula"]
)

if st.button("✅ Controleer formule"):
    if is_formula_correct(problem["shape"], formula):
        st.session_state.formula_ok = True
        st.session_state.feedback_formula = "✅ Correcte formule!"
    else:
        st.session_state.formula_ok = False
        st.session_state.feedback_formula = (
            "❌ Niet helemaal. Denk aan de juiste letters en volgorde.\n\n"
            f"Tip voor deze vorm: **{problem['expected_formula']}**"
        )

# Feedback formule
if st.session_state.feedback_formula:
    if st.session_state.formula_ok:
        st.success(st.session_state.feedback_formula)
    else:
        st.error(st.session_state.feedback_formula)

# Stap 2: numeriek antwoord
st.subheader("Stap 2 — Bereken de inhoud (tot op de eenheid)")
if not st.session_state.formula_ok:
    st.info("⚠️ Eerst de juiste **formule** invullen en laten controleren.")
else:
    answer = st.number_input(
        f"Jouw antwoord (in {problem['units']})",
        min_value=0,
        step=1,
        key="answer_input"
    )
    if st.button("🧮 Controleer antwoord"):
        correct = problem["volume"]
        if answer == correct:
            st.session_state.feedback_answer = f"🎉 Helemaal juist! **{correct} {problem['units']}**."
        else:
            st.session_state.feedback_answer = (
                f"❌ Niet juist. Probeer nog eens.\n\n"
                f"Wil je de uitwerking zien? Klap hieronder open."
            )

# Feedback antwoord
if st.session_state.feedback_answer:
    if st.session_state.feedback_answer.startswith("🎉"):
        st.success(st.session_state.feedback_answer)
    else:
        st.error(st.session_state.feedback_answer)

# Uitwerking (optioneel)
with st.expander("🔍 Toon uitwerking"):
    shape = problem["shape"]
    dims = problem["dimensions"]
    units = problem["units"]
    if shape == "kubus":
        z = dims["z"]
        st.markdown(
            f"""
            **Formule:** V = z³  
            **Invullen:** V = {z}³ = {z} × {z} × {z}  
            **Rekenwerk:** V = {z*z*z}  
            **Antwoord:** **{problem['volume']} {units}**
            """
        )
    elif shape == "balk":
        l, b, h = dims["l"], dims["b"], dims["h"]
        st.markdown(
            f"""
            **Formule:** V = l × b × h  
            **Invullen:** V = {l} × {b} × {h}  
            **Rekenwerk:** V = {l*b*h}  
            **Antwoord:** **{problem['volume']} {units}**
            """
        )
    else:
        b, h, L = dims["b"], dims["h"], dims["L"]
        area = (b * h) / 2
        st.markdown(
            f"""
            **Formule:** V = (b × h / 2) × L  
            **Driehoekige doorsnede:** A = (b × h) / 2 = ({b} × {h}) / 2 = {area:g} cm²  
            **Invullen:** V = {area:g} × {L}  
            **Rekenwerk:** V = {int(round(area * L))}  
            **Antwoord:** **{problem['volume']} {units}**
            """
        )

st.divider()
st.caption("🧠 Tip: rond af **tot op de eenheid** (we kiezen hier integere maten, dus het volume komt uit in hele cm³).")
