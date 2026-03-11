import streamlit as st
import random
import time

# =====================================================
#   ZELDZAME DIERLIJST (20 dieren, 4 per klasse)
# =====================================================

def generate_animals():
    mammals = [
        "Pangolin",
        "Seneca white deer",
        "Elephant shrew",
        "Vaquita"
    ]

    fish = [
        "American Brook Lamprey",
        "Shortnose Sturgeon",
        "Maryland Darter",
        "Atlantic Hawksbill Seaturtle"  # aquatisch maar bron-onderbouwd
    ]

    amphibians = [
        "Blue-spotted Salamander",
        "Green Salamander",
        "Mountain Chorus Frog",
        "Eastern Hellbender"
    ]

    reptiles = [
        "Loggerhead Seaturtle",
        "Kemp’s Ridley Seaturtle",
        "Leatherback Seaturtle",
        "Appalachian Blind Snake"
    ]

    birds = [
        "Appalachian Bewick’s Wren",
        "Bald Eagle",
        "Northern Goshawk",
        "Northern Saw-whet Owl"
    ]

    all_animals = mammals + fish + amphibians + reptiles + birds
    random.shuffle(all_animals)
    return all_animals


# =====================================================
#   STREAMLIT UI
# =====================================================

st.set_page_config(page_title="Draaiend Rad – Zeldzame Dieren", page_icon="🎡")

st.title("🎡 Rad van Fortuin – Zeldzame Dieren")

# Initialiseer state
if "animals" not in st.session_state:
    st.session_state.animals = generate_animals()

if "winner" not in st.session_state:
    st.session_state.winner = None


# ===========================================
#   Knop: Nieuwe lijst dieren
# ===========================================

if st.button("🔄 Genereer 20 nieuwe zeldzame dieren"):
    st.session_state.animals = generate_animals()
    st.session_state.winner = None
    st.success("Nieuwe dieren gegenereerd!")


# Toon de lijst
st.subheader("🦓 Dieren op het rad")
st.write(", ".join(st.session_state.animals))


# ===========================================
#   Knop: Draai het rad!
# ===========================================

if st.button("🎯 Draai het rad!"):
    placeholder = st.empty()

    # draai-animatie
    for i in range(35):
        current = random.choice(st.session_state.animals)
        placeholder.markdown(f"## 🎡 Draait... → **{current}**")
        time.sleep(0.06 + i * 0.005)

    # uiteindelijk resultaat
    result = random.choice(st.session_state.animals)
    st.session_state.winner = result
    placeholder.markdown(f"# 🎉 Het rad stopt op: **{result}**! 🎉")

    # confetti
    st.balloons()


# ===========================================
#   resultaat tonen
# ===========================================

if st.session_state.winner:
    st.success(f"🎉 Geselecteerd dier: **{st.session_state.winner}**")