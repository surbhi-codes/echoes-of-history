import html
import ollama
import streamlit as st

MODEL = "gemma3:4b"  # use the exact name from `ollama list`

SYSTEM = (
    "You are a careful, respectful historical storyteller. You write fiction inspired by real events. "
    "Never invent specific dates, statistics or named people. If you are unsure of a fact, "
    "stay general instead of guessing."
)

EVENTS = {
    "Salt March (1930)": "the Salt March led by Mahatma Gandhi in 1930",
    "Indian independence (1947)": "India's independence on 15 August 1947",
    "Great Fire of London (1666)": "the Great Fire of London in 1666",
    "Apollo 11 Moon landing (1969)": "the Apollo 11 Moon landing in 1969",
    "Fall of the Berlin Wall (1989)": "the fall of the Berlin Wall in 1989",
    "Custom event": None,
}

PERSPECTIVES = [
    "an ordinary person who lived through it",
    "a young student",
    "a shopkeeper in the market",
    "a child watching from a rooftop",
    "a village elder",
    "a newspaper reporter",
    "Custom...",
]

STYLES = {
    "First-person narration": "first-person narration",
    "Short story": "short story with a beginning, middle and end",
    "Diary entry": "diary entry written that same night",
    "Letter to a loved one": "letter written to a loved one far away",
}


def ask_model(messages):
    try:
        with st.spinner("Listening for the echo... the first answer can take a while"):
            reply = ollama.chat(model=MODEL, messages=messages)
        return reply["message"]["content"]
    except Exception as e:
        st.error(f"Could not reach the model. Is Ollama running? Details: {e}")
        return None


def to_html(text):
    paras = [html.escape(p.strip()).replace("\n", "<br>") for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{p}</p>" for p in paras)


st.set_page_config(page_title="Echoes of History", page_icon="📜")
st.session_state.setdefault("chronicle", [])

st.markdown(
    """
    <style>
    h1 { text-align: center; letter-spacing: 2px; border-bottom: 3px double #7b2d26; padding-bottom: 0.4rem; }
    .echo-box { background: #fbf5e6; border: 1px solid #b89b5e; border-left: 6px solid #7b2d26;
                padding: 0.6rem 1.2rem; border-radius: 4px; line-height: 1.7; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Echoes of History")
st.caption(f"Runs fully on this laptop using {MODEL} via Ollama. No internet, no account, no cost.")

choice = st.selectbox("Pick a moment in history", list(EVENTS))
if choice == "Custom event":
    event = st.text_input("Describe the event", "the first train arriving in a small town")
else:
    event = EVENTS[choice]

pick = st.selectbox("Through whose eyes?", PERSPECTIVES)
who = st.text_input("Describe the narrator", "a street vendor") if pick == "Custom..." else pick

style = st.selectbox("Style", list(STYLES))

if st.button("Hear the echo"):
    prompt = f"Write a {STYLES[style]} of about 150 words about {event}, from the point of view of {who}."
    text = ask_model([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
    if text:
        st.session_state["echo"] = text
        st.session_state["context"] = (event, who)
        st.session_state["qa"] = []
        title = choice if choice != "Custom event" else event
        st.session_state["chronicle"].append({"title": f"{title} - {style}", "text": text})

if "echo" in st.session_state:
    st.subheader("The echo")
    st.markdown(f'<div class="echo-box">{to_html(st.session_state["echo"])}</div>', unsafe_allow_html=True)
    st.caption("Fiction inspired by history. A small model can get facts wrong, so verify before relying on it.")
    st.download_button("Download this echo (.txt)", data=st.session_state["echo"], file_name="echo.txt")

    question = st.text_input("Ask this voice a question")
    if st.button("Ask") and question:
        ev, wh = st.session_state["context"]
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": (
                f"Event: {ev}. You are {wh}. You earlier said: {st.session_state['echo']}\n\n"
                f"Answer in character, in under 80 words: {question}")},
        ]
        answer = ask_model(msgs)
        if answer:
            st.session_state["qa"].append((question, answer))

    for q, a in st.session_state["qa"]:
        st.markdown(f"**You:** {q}")
        st.write(a)

with st.sidebar:
    st.header("Chronicle")
    st.caption("Echoes from this session")
    for item in reversed(st.session_state["chronicle"]):
        with st.expander(item["title"]):
            st.write(item["text"])