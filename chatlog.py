"""Anonymous logging + privacy redaction.

What is saved: time, a random session id, which dorm link was used, language,
the question (with personal numbers removed), the answer, and the 👍/👎 rating.
What is NOT saved: names, phone numbers, IP addresses, WhatsApp numbers.

Logs always go to logs/chat_log.csv. If a Google Sheet is set up in secrets
(README step 6), they also go there - do this before the pilot, because the
free Streamlit hosting deletes local files whenever the app restarts or sleeps.
"""

import csv
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "chat_log.csv"
COLUMNS = ["time_sgt", "session", "dorm", "lang", "event", "msg_id", "question", "answer", "rating"]
SGT = timezone(timedelta(hours=8))

# Helpline numbers from the resource sheet are allowed through; any other long number is removed.
ALLOWED_NUMBERS = {"65362692", "64385122", "62477001", "6562477001"}

FIN_PATTERN = re.compile(r"\b[STFGM]\d{7}[A-Z]\b", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
LONG_NUMBER_PATTERN = re.compile(r"\+?\d[\d\s-]{6,}\d")


def redact(text: str) -> str:
    """Remove FIN/NRIC numbers, emails and phone/ID numbers (8+ digits) from text."""
    text = FIN_PATTERN.sub("[ID removed]", text)
    text = EMAIL_PATTERN.sub("[email removed]", text)

    def _number(match):
        digits = re.sub(r"\D", "", match.group())
        if digits in ALLOWED_NUMBERS or len(digits) < 8:
            return match.group()
        return "[number removed]"

    return LONG_NUMBER_PATTERN.sub(_number, text)


_sheet_warning_shown = False


def _google_sheet():
    """Return the Google Sheet worksheet if it's configured, else None."""
    global _sheet_warning_shown
    try:
        import streamlit as st

        if "gcp_service_account" not in st.secrets or "LOG_SHEET_URL" not in st.secrets:
            return None

        @st.cache_resource
        def _open(url):
            import gspread

            client = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
            sheet = client.open_by_url(url).sheet1
            if not sheet.row_values(1):
                sheet.append_row(COLUMNS)
            return sheet

        return _open(st.secrets["LOG_SHEET_URL"])
    except Exception as e:  # logging must never break the chat
        if not _sheet_warning_shown:
            print(f"[chatlog] Google Sheet not set up, logging to CSV only ({type(e).__name__})")
            _sheet_warning_shown = True
        return None


def log_event(**fields):
    row = {col: "" for col in COLUMNS}
    row.update({k: v for k, v in fields.items() if k in row})
    row["time_sgt"] = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S")

    LOG_FILE.parent.mkdir(exist_ok=True)
    is_new = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)

    sheet = _google_sheet()
    if sheet is not None:
        try:
            sheet.append_row([str(row[c]) for c in COLUMNS])
        except Exception as e:
            print(f"[chatlog] Could not write to Google Sheet: {e}")
