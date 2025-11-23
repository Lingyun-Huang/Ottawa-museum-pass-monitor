import os
import time
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Nature museum pass availability API

PASS_INFO = [
    {
        "title": "Science Museum Pass",
        "url": "https://gateway.bibliocommons.com/v2/libraries/ottawa/bibs/S26C1082166/availability?locale=en-CA",
        "description": "Canadian Aviation and Space Museum, Canada Agriculture and Food Museum, "
                       "Canada Science and Technology Museum"
    },
    {
        "title": "Nature Museum Pass",
        "url": "https://gateway.bibliocommons.com/v2/libraries/ottawa/bibs/S26C369552/availability?locale=en-CA",
        "description": "Canadian Museum of Nature"
    }
]

TARGET_STATUS = "AVAILABLE_NOT_HOLDABLE"

TARGET_BRANCHES = os.getenv("TARGET_BRANCHES")
if TARGET_BRANCHES:
    TARGET_BRANCHES = set(branch.strip() for branch in TARGET_BRANCHES.split(","))
else:
    TARGET_BRANCHES = {"Main", "Beaverbrook"}

CHECK_INTERVAL = os.getenv("CHECK_INTERVAL")
if CHECK_INTERVAL:
    CHECK_INTERVAL = int(CHECK_INTERVAL)
else:
    CHECK_INTERVAL = 60 * 5  # 5 min

FOUND_RECHECK_INTERVAL = os.getenv("FOUND_RECHECK_INTERVAL")
if FOUND_RECHECK_INTERVAL:
    FOUND_RECHECK_INTERVAL = int(FOUND_RECHECK_INTERVAL)
else:
    FOUND_RECHECK_INTERVAL = 60 * 60 * 24  # 1 day


# ---------------------------
# Email sending function
# ---------------------------
def send_email_alert(summary_lines):
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    receiver = os.getenv("EMAIL_TO")

    if not sender or not password or not receiver:
        logger.info("Missing environment variables for email. Please set GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_TO.")
        return

    subject = "Ottawa Library Museum Pass Alert"
    summary_lines.append("""
More info at https://collections.biblioottawalibrary.ca/en/access-passes-including-museum-passes

Library Hours:
    Monday: 10:00 am - 9:00 pm
    Tuesday: 10:00 am - 9:00 pm
    Wednesday: 10:00 am - 9:00 pm
    Thursday: 10:00 am - 9:00 pm
    Friday: 10:00 am - 6:00 pm
    Saturday: 10:00 am - 5:00 pm
    Sunday: 10:00 am - 5:00 pm 
    """)
    body = "\n".join(summary_lines)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    logger.info("Sending email alert...")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver.split(','), msg.as_string())
        logger.info("Email sent!")
    except Exception as e:
        logger.info("Email sending failed:", e)


# ---------------------------
# Fetch and parse availability
# ---------------------------
def fetch_availability(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.info(f"[{datetime.now()}] Error fetching {url}:", e)
        return None


def check_pass_availability(pass_info):
    """Return dict: branch -> number of copies"""
    url = pass_info["url"]
    data = fetch_availability(url)
    branch_counts = defaultdict(int)

    if not data:
        return branch_counts

    items = data.get("entities", {}).get("bibItems", {})
    for item_id, item in items.items():
        branch = item.get("branchName", "")
        status = item.get("availability", {}).get("libraryStatus", "")
        if branch in TARGET_BRANCHES and status == TARGET_STATUS:
            branch_counts[branch] += 1

    return branch_counts


# ---------------------------
# Main loop
# ---------------------------
def main():
    logger.info("Monitoring passes for 'AVAILABLE_NOT_HOLDABLE'...\n")

    while True:
        alert_lines = []
        for pass_info in PASS_INFO:
            branch_counts = check_pass_availability(pass_info)
            for branch, count in branch_counts.items():
                line = f"Found {count} {pass_info['title']} at {branch} library, you can use it to access {pass_info['description']}."
                alert_lines.append(line)
                logger.info(f"[{datetime.now()}] {line}")

        if alert_lines:
            logger.info("ALERT! Copies are AVAILABLE_NOT_HOLDABLE!")
            send_email_alert(alert_lines)

            time.sleep(FOUND_RECHECK_INTERVAL)
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
