import streamlit as st
import random

# =========================
# Hulpfuncties
# =========================

def rnd():
    """Genereert een waarde met maximaal 2 decimalen."""
    return round(random.uniform(0.5, 50), 2)

def sig_decimals(x):
    """Aantal decimalen voor beduidende cijfers."""
    s = f"{x}"
    return len(s.split(".")[1]) if "." in s else 0


def generate_problem():
    """Genereert een situatie en bepaalt welke grootheid gezocht wordt."""
    g_const = 9.81
    m = rnd()
    F = round(m * g_const, 2)

    sought = random.choice(["F", "m", "g"])

    if sought == "F":
        situation = (
            f"Een voorwerp met massa **{m} kg** bevindt zich in een zwaarteveld van **9,81 N/kg**. "
            f"Bereken de kracht waarmee het wordt aangetrokken."
        )
        decimals = max(sig_decimals(m), sig_dec_decimals(g_const))
        solution = round(m * g_const, decimals)
        options = ["F = m.g", "F = m/g", "F = g/m", "F = m+g"]
        correct = "F = m.g"

    elif sought == "m":
        situation = (
            f"Een voorwerp ondervindt een kracht van **{F} N** in een zwaarteveld van **9,81 N/kg**. "
            f"Bereken de massa van het voorwerp."
        )
        decimals = max(sig_decimals(F), sig_decimals(g_const))
        solution = round(F / g_const, decimals)
        options = ["m = F/g", "m = F.g", "m = g/F", "m = F-g"]
        correct = "m = F/g"

    else:  # sought == "g"
        situation = (
            f"Een voorwerp met massa **{m} kg** ondervindt een kracht van **{F} N**. "
            f"Bereken de zwaarteveldsterkte op die plaats."
        )
        decimals = max(sig_decimals(F), sig_decimals(m))
        solution = round(F / m, decimals)
        options = ["g = F/m", "g = F.m", "g = m/F", "g = F+m"]
        correct = "g = F/m"

    return {
        "situation": situation,
        "sought": sought,
        "solution": solution,
        "decimals": decimals,
        "options": options,
        "correct_option": correct
    }


def reset():
    st.session_state.problem = generate_problem()
    st.session_state.formula_ok = False
    st.session_state.feedback_formula = ""
    st.session_state.feedback_answer = ""
    st.session_state.selected_formula = None
    st.session_state.answer_input = ""


# =========================
# Scorebord initialisatie
# =========================

if "score_total" not in st.session_state:
    st.session_state.score_total = 0
    st.session_state.score_formula_correct = 0
    st.session_state.score_answer_correct = 0


def reset_score():
    st.session_state.score_total = 0
    st.session_state.score_formula_correct = 0
    st.session_state.score_answer_correct = 0


# =========================
# UI
# =========================

st.set_page_config(page_title="Zwaarteveldsterkte – Oefenen", page_icon="🌍")
st.title("🌍 Oefeningen over de zwaarteveldsterkte")

# Scorebord
st.sidebar.title("📊 Scorebord")
st.sidebar.write(f"🔢 Oefeningen gemaakt: **{st.session_state.score_total}**")
st.sidebar.write(f"🧠 Juiste formules: **{st.session_state.score_formula_correct}**")
st.sidebar.write(f"🎯 Juiste antwoorden: **{st.session_state.score_answer_correct}**")

if st.sidebar.button("🔁 Reset score"):
    reset_score()
    st.sidebar.success("Score werd gereset!")

# Init oefening
if "problem" not in st.session_state:
    reset()

problem = st.session_state.problem

# Nieuwe oefening
if st.button("🔄 Nieuwe oefening"):
    reset()
    st.rerun()


# =========================
# Situatie
# =========================

st.subheader("Situatie")
st.write(problem["situation"])
st.write(f"👉 Gevraagd: **{problem['sought']}**")

# =========================
# FORMULE meerkeuze
# =========================

st.subheader("Stap 1 — Kies de juiste formule (met '.')")

options_shuffled = problem["options"][:]
random.shuffle(options_shuffled)

st.session_state.selected_formula = st.radio(
    "Welke formule gebruik je?",
    options_shuffled,
    key="formula_radio"
)

if st.button("Controleer formule"):
    st.session_state.score_total += 1  # elke poging telt als oefening

    if st.session_state.selected_formula == problem["correct_option"]:
        st.session_state.formula_ok = True
        st.session_state.feedback_formula = "✅ De formule is correct!"

        # SCORE UP
        st.session_state.score_formula_correct += 1
    else:
        st.session_state.formula_ok = False
        st.session_state.feedback_formula = "❌ Dat is niet de juiste formule."

# Feedback formule
if st.session_state.feedback_formula:
    if st.session_state.formula_ok:
        st.success(st.session_state.feedback_formula)
    else:
        st.error(st.session_state.feedback_formula)


# =========================
# ANTWOORD
# =========================

st.subheader("Stap 2 — Bereken het antwoord")

if not st.session_state.formula_ok:
    st.info("Kies en controleer eerst de juiste formule.")
else:
    st.write(f"✏️ Rond af tot **{problem['decimals']} cijfers na de komma**.")

    answer_text = st.text_input(
        "Jouw antwoord (max 2 decimalen)",
        value="",
        key="answer_input",
        placeholder="vb. 12.34"
    )

    def is_valid_answer(text):
        if text.strip() == "":
            return False
        try:
            float(text)
        except:
            return False
        if "." in text and len(text.split(".")[1]) > 2:
            return False
        return True

    if st.button("Controleer antwoord"):

        if not is_valid_answer(answer_text):
            st.session_state.feedback_answer = (
                "❌ Ongeldig antwoord. Gebruik maximaal **2 cijfers na de komma**."
            )
        else:
            answer = float(answer_text)
            tol = 10**(-problem["decimals"])

            if abs(answer - problem["solution"]) < tol:
                st.session_state.feedback_answer = (
                    f"🎉 Juist! Het antwoord is **{problem['solution']}**."
                )
                st.session_state.score_answer_correct += 1
            else:
                st.session_state.feedback_answer = (
                    f"❌ Fout. Het juiste antwoord is **{problem['solution']}**."
                )

# Feedback antwoord
if st.session_state.feedback_answer:
    if st.session_state.feedback_answer.startswith("🎉"):
        st.success(st.session_state.feedback_answer)
    else:
        st.error(st.session_state.feedback_answer)