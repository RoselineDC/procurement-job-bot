import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.mime.text import MIMEText

# ---------- CONFIG ----------
SEARCH_URL = "https://za.indeed.com/jobs?q=procurement+tender+administrator&l=South+Africa"
MAX_JOBS = 5

EMAIL_FROM = "your_email@gmail.com"
EMAIL_TO = "your_email@gmail.com"
EMAIL_PASSWORD = "YOUR_APP_PASSWORD"

GOOGLE_SHEET_NAME = "Daily Tender & Procurement Jobs"

# ---------- GOOGLE SHEETS ----------
def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "google_credentials.json", scope
    )
    client = gspread.authorize(creds)
    return client.open(GOOGLE_SHEET_NAME).sheet1

# ---------- JOB SCRAPER ----------
def scrape_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(SEARCH_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    for job in soup.select(".job_seen_beacon")[:MAX_JOBS]:
        title = job.select_one("h2").text.strip()
        company = job.select_one(".companyName").text.strip()
        location = job.select_one(".companyLocation").text.strip()
        link = "https://za.indeed.com" + job.select_one("a")["href"]

        keywords = [
            "tender submission",
            "compliance",
            "RFQ/RFP",
            "document control",
            "deadline management"
        ]

        jobs.append([
            datetime.today().strftime("%Y-%m-%d"),
            title,
            company,
            location,
            "0–3 years",
            link,
            *keywords
        ])

    return jobs

# ---------- EMAIL ----------
def send_email(df):
    html = df.to_html(index=False)
    msg = MIMEText(html, "html")
    msg["Subject"] = f"Daily Procurement & Tender Jobs – {datetime.today().date()}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

# ---------- MAIN ----------
def main():
    sheet = connect_sheet()
    jobs = scrape_jobs()

    df = pd.DataFrame(jobs, columns=[
        "Date",
        "Job Title",
        "Company",
        "Location",
        "Experience",
        "Link",
        "Keyword 1",
        "Keyword 2",
        "Keyword 3",
        "Keyword 4",
        "Keyword 5"
    ])

    for row in jobs:
        sheet.append_row(row)

    send_email(df)

if __name__ == "__main__":
    main()
