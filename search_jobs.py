import requests
from bs4 import BeautifulSoup
from datetime import date
import smtplib
from email.mime.text import MIMEText
import os

# ---------------- CONFIG ----------------
SEARCH_URL = "https://za.indeed.com/jobs?q=procurement+tender+administrator&l=South+Africa"
MAX_JOBS = 15



EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]


# ---------------- SCRAPE JOBS ----------------
def scrape_jobs():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(SEARCH_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    rows = []

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

        rows.append([
            str(date.today()),
            title,
            company,
            location,
            "0–3 years",
            link,
            *keywords
        ])

    return rows

# ---------------- SEND EMAIL ----------------
def send_email(rows):
    header = (
        "Date | Job Title | Company | Location | Experience | Link | "
        "Keyword1 | Keyword2 | Keyword3 | Keyword4 | Keyword5\n"
    )

    body = header + "\n".join([" | ".join(row) for row in rows])

    msg = MIMEText(body)
    msg["Subject"] = f"Daily Procurement & Tender Jobs – {date.today()}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

# ---------------- MAIN ----------------
def main():
    rows = scrape_jobs()
    if rows:
        send_email(rows)

if __name__ == "__main__":
    main()
