import json
import re
from datetime import datetime
from dateutil import parser
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

st.markdown("""
    <style>
    html, body, .stApp {
        height: 100%;
        margin: 0;
        padding: 0;
    }

    .stApp {
        background-image: url("https://c0.wallpaperflare.com/preview/475/1022/504/romania-rar%C4%83u-foggy-clean.jpg");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        padding-top: 5vh;
    }

    .block-container {
        background-color: rgba(255, 255, 255, 0.88);
        padding: 2rem;
        border-radius: 15px;
        max-width: 800px;
        margin: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .main-title {
        color: #2c3e50;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
    }

    .description {
        font-size: 18px;
        color: #34495e;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


# Load class schedule
with open("calendar_data.json", "r") as file:
    events = json.load(file)

# --- Utility Functions ---
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_events_for_day(day_name):
    matching = [e for e in events if e["day"].lower() == day_name.lower()]
    if not matching:
        return f"No subjects scheduled for {day_name}."
    return "\n".join([
        f"- **{e['subject']}** from *{e['start_time']}* to *{e['end_time']}* in `{e['room']}`"
        for e in matching
    ])


def detect_day_in_input(text):
    for day in DAYS:
        if day.lower() in text.lower():
            return day
    return None


def extract_date_from_input(text):
    match = re.search(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
        text.lower())
    if match:
        try:
            dt = parser.parse(match.group(0))
            return dt
        except:
            return None
    return None


def get_schedule_for_input(user_input):
    extracted_date = extract_date_from_input(user_input)
    if extracted_date:
        day = extracted_date.strftime("%A")
        full_date = extracted_date.strftime("%B %d, %Y")
        return day, full_date, get_events_for_day(day)

    detected_day = detect_day_in_input(user_input)
    if detected_day:
        return detected_day, None, get_events_for_day(detected_day)

    today = datetime.today()
    return today.strftime("%A"), today.strftime("%B %d, %Y"), get_events_for_day(today.strftime("%A"))


# Prompt template
template = """
You are a calendar assistant.

Respond clearly and truthfully based on the user's question and the schedule provided.

If a full calendar date is given (like July 13), tell the user what day of the week it is.
Do not invent subjects or rooms — only use the schedule data given.

User's question: "{user_input}"

Date interpreted: {full_date}
Day: {day}
Schedule for {day}:
{calendar_events}

Now answer the user's question clearly using the info above.
"""

prompt = PromptTemplate(
    input_variables=["user_input", "day", "full_date", "calendar_events"],
    template=template
)

llm = OllamaLLM(model="llama3")
chain = prompt | llm

# --- Main UI ---
st.markdown("<h1 class='main-title'>📅 AI Calendar Assistant </h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='description'>Your personal calendar assistant for days and schedules — fully offline, responsive, and smart.</p>",
    unsafe_allow_html=True)
st.markdown("---")

with st.expander("📚 What this app can do"):
    st.markdown("""
    - 🔍 Understand what event you have on any **weekday** or **specific date**
    - 🕘 Show class times and room locations
    - 💬 Understand questions like:
        - "What subject do I have on Wednesday?"
        - "Where is my class on July 13?"
        - "Do I have any class on Saturday?"
        - "What day is it on June 30?"
    - ✅ Works fully **offline** using mock schedule
    """)

st.markdown("&nbsp;", unsafe_allow_html=True)

# 📝 Question Box
st.markdown("### How can I help you?")
user_input = st.text_area("Input below:", height=100)

if st.button("💬 Ask the Assistant"):
    if user_input:
        day, full_date, events_text = get_schedule_for_input(user_input)
        full_date_str = full_date if full_date else ""
        response = chain.invoke({
            "user_input": user_input,
            "day": day,
            "full_date": full_date_str,
            "calendar_events": events_text
        })

        st.markdown(f"**📅 Date:** {full_date or day}")
        st.markdown("### 🤖 Assistant says:")
        st.markdown(f"<div style='background-color:#f1f3f6; padding:15px; border-radius:10px;'>{response}</div>",
                    unsafe_allow_html=True)
    else:
        st.warning("Please enter a question.")


st.markdown("---")
st.caption("• Powered by Ollama + LangChain + Streamlit")

with st.sidebar:
    st.image(
        "https://scontent.fmnl30-1.fna.fbcdn.net/v/t39.30808-6/308119466_587186839860204_651741802680084912_n.png?_nc_cat=103&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=PMkxDHKJy04Q7kNvwGDUJNS&_nc_oc=AdkVdbC__QwIhh782C_qTvjHogeoKXvhqXeqV3twMLi40m0s3k13gro8hKw8AA6Tsqc&_nc_zt=23&_nc_ht=scontent.fmnl30-1.fna&_nc_gid=Y8N6cveFm5Cy0jGRAQk6EQ&oh=00_AfPmAUdqf62j6BqYjabYrOTXgUS2Z86vBPEyEoSE8rDdRw&oe=6862CE44",
        width=120)
    st.markdown("Calendar Assistant")
    st.markdown("• Works offline")
    st.markdown("• Uses mock schedule data")

