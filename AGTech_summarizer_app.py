# AGTech_summarizer_app.py
# PID 4037595
# nohup streamlit run AGTech_summarizer_app.py \
#   --server.port 8555 \
#   --server.address 172.10.0.181 \
#   --server.fileWatcherType none \
#   > streamlit_app.log 2>&1 &

import streamlit as st
import json
import time
import os
from researcher import run_research
from summarizer import run_summary
from PIL import Image

# ------------------ UI HEADER LOGO ------------------
logo = Image.open("/home/datascience/AGTech/logoAGtech.png")
logo = logo.resize((100, 40))
st.image(logo)

st.title("🌾 AGTech Crop Disease Research + LLM Summary App")

input_data = st.text_area("Paste JSON Input", height=300)

# Create the logs folder if not exists
os.makedirs("run_logs", exist_ok=True)

# Single combined log file
LOG_FILE = "run_logs/app_log.txt"


if st.button("Summarise Disease Info"):

    if not input_data.strip():
        st.error("Please paste valid JSON input.")
        st.stop()

    # Timestamp for logs
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------
    # Validate JSON
    # --------------------------
    try:
        data = json.loads(input_data)
    except Exception as e:
        st.error(f"Invalid JSON format: {e}")
        st.stop()

    # --------------------------
    # STEP 1 — RUN RESEARCH PIPELINE
    # --------------------------
    st.write("🔎 Gathering Data About the Disease…")

    try:
        csv_file = run_research(data)
        st.success(f"CSV created: {csv_file}")
    except Exception as e:
        st.error(f"Error during Research Pipeline: {e}")
        st.stop()

    # --------------------------
    # STEP 2 — RUN SUMMARIZER PIPELINE
    # --------------------------
    st.write("🧠 Running LLM Summarizer…")

    try:
        summary_file, summary_text, summary_json = run_summary(csv_file, data)
    except Exception as e:
        st.error(f"Error during Summarization Pipeline: {e}")
        st.stop()

    st.success("Summary Completed!")

    # --------------------------
    # APPEND INPUT + SUMMARY TO SINGLE LOG FILE
    # --------------------------
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("\n\n=================================================\n")
        log.write(f"===== RUN {timestamp} =====\n\n")
        log.write("--- INPUT JSON ---\n")
        log.write(json.dumps(data, indent=4))
        log.write("\n\n--- SUMMARY OUTPUT ---\n")
        log.write(summary_text)
        log.write("\n=================================================\n")

    # --------------------------
    # DISPLAY SUMMARY
    # --------------------------
    st.subheader("Summariese Disease Info")
    st.markdown(summary_text)


