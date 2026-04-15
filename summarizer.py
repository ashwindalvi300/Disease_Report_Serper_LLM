# summarizer.py

import csv
import json
import re
import os
from llm_client import chat_llm


# ---------------------------------------------------------
# Extract JSON from LLM output
# ---------------------------------------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            return None

    return None


# ---------------------------------------------------------
# Load CSV content grouped by (Crop Type, Disease)
# ---------------------------------------------------------
def load_research(csv_file):
    output = {}

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["Crop Type"], row["Disease"])

            output.setdefault(key, []).append({
                "title": row["Result Title"],
                "link": row["Result Link"],
                "snippet": row["Snippet"],
                "page_content": row["Page Content"]
            })

    return output


# ---------------------------------------------------------
# Build LLM Prompt
# ---------------------------------------------------------
def build_prompt(field_data, crop, disease, pages):

    prompt = f"""
Analyze the disease **{disease}** in **{crop}** using field data and the scraped online sources.

FIELD DATA:
{json.dumps(field_data, indent=2)}

SCRAPED RESULTS:
"""
    for i, p in enumerate(pages):
        prompt += f"""
--------
SOURCE #{i+1}
Title: {p['title']}
URL: {p['link']}
Snippet: {p['snippet']}
Content:
{p['page_content']}
"""

    prompt += """
Return STRICT JSON ONLY with this structure:

{
  "disease": "...",
  "crop": "...",
  "Summary": {
    "Common Causes": [...],
    "Organic Treatments": [...],
    "Chemical Control Methods": [...],
    "Future Prevention": [...],
    "Remedies": [...],
    "Additional Insights": [...]
  }
}
"""

    return prompt



# ---------------------------------------------------------
# MAIN SUMMARIZER PIPELINE
# ---------------------------------------------------------
def run_summary(csv_file, field_data):

    research_data = load_research(csv_file)

    combined_json = {}
    summary_text = ""

    # Create output folders
    os.makedirs("disease_outputs", exist_ok=True)
    os.makedirs("json_summaries", exist_ok=True)
    os.makedirs("txt_summaries", exist_ok=True)

    crop_header_added = False

    # Prepare filenames using grower, crop, date
    grower = field_data["Grower Name"].replace(" ", "_")
    crop = field_data["Crop Type"].replace(" ", "_")
    report_date = field_data["Report Date"].replace(" ", "_")

    txt_filename = f"txt_summaries/Summary_{grower}_{crop}_{report_date}.txt"
    json_filename = f"json_summaries/Summary_{grower}_{crop}_{report_date}.json"

    # ---------------------------------------------------------
    # PROCESS EACH DISEASE
    # ---------------------------------------------------------
    for (crop_type, disease), pages in research_data.items():

        prompt = build_prompt(field_data, crop_type, disease, pages)
        raw = chat_llm(prompt)
        parsed = extract_json(raw)

        # Crop header once
        if not crop_header_added:
            summary_text += f"\n\n**===== CROP TYPE : {crop_type.upper()} =====**\n"
            crop_header_added = True

        # Disease header
        summary_text += f"\n**===== DISEASE : {disease.upper()} =====**\n"

        if not parsed:
            summary_text += "LLM FAILED FOR THIS DISEASE.\n"
            continue

        combined_json[disease] = parsed

        # Save individual disease JSON
        safe = disease.replace(" ", "_")
        with open(f"disease_outputs/{safe}.json", "w", encoding="utf-8") as df:
            json.dump(parsed, df, indent=4)

        # Append readable summary
        for key, values in parsed["Summary"].items():
            summary_text += f"\n**{key}**\n"
            for v in values:
                summary_text += f"- {v}\n"

    # ---------------------------------------------------------
    # SAVE FINAL JSON & TXT INTO SEPARATE FOLDERS
    # ---------------------------------------------------------
    with open(json_filename, "w", encoding="utf-8") as jf:
        json.dump(combined_json, jf, indent=4)

    with open(txt_filename, "w", encoding="utf-8") as tf:
        tf.write(summary_text)

    return txt_filename, summary_text, combined_json
