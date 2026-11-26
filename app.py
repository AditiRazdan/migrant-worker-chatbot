"""Catalyst Bot - a chat that answers migrant workers' questions from the official resource sheet.

Run locally:   streamlit run app.py
Dorm links:    add ?dorm=A or ?dorm=B to the URL so you can compare the two dorms in the logs.
"""

import uuid

import streamlit as st

from chatlog import log_event, redact
from llm import stream_answer
from prompts import build_system_prompt
from ui_text import LANGUAGES, TEXT

MAX_QUESTIONS_PER_SESSION = 30  # protects your API budget
HISTORY_MESSAGES = 12  # how much of the conversation the AI sees (so follow-up questions work)
MAX_QUESTION_CHARS = 1000

st.set_page_config(page_title="Migrant Worker Bot", page_icon="💬", layout="centered")
st.markdown(
    """<style>
    #MainMenu, footer {visibility: hidden;}
    div.stButton > button {font-size: 1.15rem; padding: 0.6rem 0;}
    </style>""",
    unsafe_allow_html=True,
)

ss = st.session_state
ss.setdefault("session_id", uuid.uuid4().hex[:10])  # random, not linked to the person
ss.setdefault("lang", None)
ss.setdefault("messages", [])  # each: {"role", "content", "id"}
dorm = st.query_params.get("dorm", "")


def log(**fields):
    log_event(session=ss.session_id, dorm=dorm, lang=ss.lang, **fields)


def choose_language(code):
    ss.lang = code
    ss.messages = []


def reset_language():
    ss.lang = None
    ss.messages = []


def on_rating(msg_id):
    value = ss.get(f"fb_{msg_id}")
    log(event="rating", msg_id=msg_id, rating={0: "down", 1: "up"}.get(value, "cleared"))


def show_feedback(msg_id):
    st.feedback("thumbs", key=f"fb_{msg_id}", on_change=on_rating, args=(msg_id,))


# ---------- Screen 1: choose a language ----------
if ss.lang is None:
    st.title("💬 Catalyst Bot")
    st.write("Choose your language · மொழியைத் தேர்ந்தெடுக்கவும் · ভাষা বেছে নিন")
    for code, name in LANGUAGES.items():
        st.button(name, key=f"lang_{code}", on_click=choose_language, args=(code,), use_container_width=True)
    st.stop()

# ---------- Screen 2: chat ----------
t = TEXT[ss.lang]
st.title("💬 Catalyst Bot")
st.error(t["emergency"])  # always visible, never depends on the AI
st.caption(t["human"])
st.button(f"🌐 {t['change_language']}", on_click=reset_language)

with st.chat_message("assistant"):
    st.markdown(t["welcome"])

for m in ss.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            show_feedback(m["id"])

questions_asked = sum(1 for m in ss.messages if m["role"] == "user")
over_limit = questions_asked >= MAX_QUESTIONS_PER_SESSION
if over_limit:
    st.info(t["limit"])

question = st.chat_input(t["placeholder"], disabled=over_limit)

if question and not over_limit:
    question = redact(question.strip())[:MAX_QUESTION_CHARS]
    ss.messages.append({"role": "user", "content": question, "id": uuid.uuid4().hex[:8]})
    with st.chat_message("user"):
        st.markdown(question)

    # Recent conversation for the AI; it must start with a user message.
    history = [{"role": m["role"], "content": m["content"]} for m in ss.messages[-HISTORY_MESSAGES:]]
    while history and history[0]["role"] != "user":
        history.pop(0)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(stream_answer(build_system_prompt(ss.lang), history))
            if not isinstance(answer, str) or not answer.strip():
                raise RuntimeError("Empty answer from the model")
        except Exception as e:
            print(f"[app] API error: {e!r}")  # shows in the Streamlit Cloud logs
            st.markdown(t["error"])
            ss.messages.pop()  # drop the unanswered question so the conversation stays valid
            log(event="error", question=question, answer=repr(e)[:300])
        else:
            msg_id = uuid.uuid4().hex[:8]
            ss.messages.append({"role": "assistant", "content": answer, "id": msg_id})
            log(event="qa", msg_id=msg_id, question=question, answer=answer)
            show_feedback(msg_id)
