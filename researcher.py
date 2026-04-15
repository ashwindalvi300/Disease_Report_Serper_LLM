# researcher.py

import json
import csv
import http.client
import os
from dotenv import load_dotenv

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


# --------------------------
# SERPER SEARCH
# --------------------------
def serper_search(query: str):
    conn = http.client.HTTPSConnection("google.serper.dev")

    payload = json.dumps({"q": query, "num": 5})

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    return json.loads(res.read().decode("utf-8"))


# --------------------------
# SERPER SCRAPE
# --------------------------
def serper_scrape(url: str):
    conn = http.client.HTTPSConnection("google.serper.dev")

    payload = json.dumps({"url": url})

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    conn.request("POST", "/scrape", payload, headers)
    res = conn.getresponse()
    return json.loads(res.read().decode("utf-8"))


# --------------------------
# MAIN RESEARCH PIPELINE
# --------------------------
def run_research(data: dict):

    # Create folder for CSV storage
    os.makedirs("csv_outputs", exist_ok=True)

    grower = data["Grower Name"].replace(" ", "_")
    crop = data["Crop Type"].replace(" ", "_")
    date = data["Report Date"].replace(" ", "_")

    csv_filename = f"csv_outputs/{grower}_{crop}_{date}.csv"

    # Create CSV and headers
    with open(csv_filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Report Date", "Field Name", "Crop Type", "Growth Stage",
            "Disease", "Severity", "Result Title", "Result Link",
            "Snippet", "Page Content"
        ])

    # Process each disease
    for item in data["Diseases"]:
        disease = item["Disease"]
        severity = item["Severity"]

        query = f"""
{disease} disease in {data["Crop Type"]} during {data["Growth Stage"]} stage,
symptoms, IDM, fungicides, organic control,
soil condition: {data["Soil Condition"]},
temperature: {data["Temp"]}, humidity: {data["Humidity"]}
"""

        search_res = serper_search(query)
        organic = search_res.get("organic", [])

        with open(csv_filename, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            for result in organic:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")

                try:
                    scraped = serper_scrape(link)
                    content = scraped.get("text", "")[:5000]
                except:
                    content = "SCRAPE_FAILED"

                writer.writerow([
                    data["Report Date"],
                    data["Field Name"],
                    data["Crop Type"],
                    data["Growth Stage"],
                    disease,
                    severity,
                    title,
                    link,
                    snippet,
                    content
                ])

    return csv_filename
