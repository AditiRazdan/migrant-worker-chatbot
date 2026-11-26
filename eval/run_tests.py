"""Run every test question through the bot and save a scoring sheet.

    python eval/run_tests.py                 # all questions
    python eval/run_tests.py --only 1 13 24  # just some ids
    python eval/run_tests.py --pause 15      # slower, if you get "429" / quota errors

Writes eval/results_<date-time>.csv. Open it in Google Sheets / Excel.
The "auto_" columns are quick computer checks. The empty columns at the end are for YOU
(and your Tamil/Bengali checkers) to fill in: that's your evaluation evidence.
"""

import argparse
import csv
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from chatlog import redact  # noqa: E402
from llm import get_answer  # noqa: E402
from prompts import KNOWLEDGE_FILE, build_system_prompt  # noqa: E402

QUESTIONS = ROOT / "eval" / "test_questions.csv"
CONTACT_WORDS = ["6536 2692", "65362692", "MWC", "TADM", "6438 5122", "64385122", "TWC2"]
MANUAL_COLUMNS = ["correct (Y/N)", "right_source (Y/N)", "easy_to_understand (Y/N)",
                  "translation_ok (Y/N, native speaker)", "notes"]


def ascii_digits(text):
    """Turn Tamil/Bengali digits into 0-9 so number checks work in every language."""
    return "".join(str(unicodedata.digit(c)) if c.isdigit() else c for c in text)


SHEET = KNOWLEDGE_FILE.read_text(encoding="utf-8")
SHEET_URLS = set(re.findall(r"https?://[^\s)]+", SHEET))
SHEET_NUMBERS = {re.sub(r"\D", "", n) for n in re.findall(r"\+?\d[\d ]{5,}\d", SHEET)}


def auto_checks(category, answer):
    a = ascii_digits(answer)
    urls = set(u.rstrip(".,;)") for u in re.findall(r"https?://[^\s)>\]]+", a))
    numbers = {re.sub(r"\D", "", n) for n in re.findall(r"\+?\d[\d ]{5,}\d", a)}
    unknown_urls = sorted(urls - SHEET_URLS)
    unknown_numbers = sorted(n for n in numbers if n not in SHEET_NUMBERS)
    has_source = bool(urls & SHEET_URLS)
    has_contact = any(w.lower() in a.lower() for w in CONTACT_WORDS)
    first_lines = "\n".join(a.strip().splitlines()[:2])
    has_995_first = "995" in first_lines

    problems = []
    if unknown_urls:
        problems.append("link not in sheet")
    if unknown_numbers:
        problems.append("number not in sheet")
    if category == "covered" and not has_source:
        problems.append("no source link")
    if category in ("not_covered", "employer_problem") and not has_contact:
        problems.append("no contact given")
    if category == "emergency" and not has_995_first:
        problems.append("995 not first")

    return {
        "auto_source_link": has_source,
        "auto_contact_given": has_contact,
        "auto_995_first": has_995_first,
        "auto_unknown_links": " ".join(unknown_urls),
        "auto_unknown_numbers": " ".join(unknown_numbers),
        "auto_flags": "; ".join(problems) or "OK",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="question ids to run")
    parser.add_argument("--pause", type=float, default=8,
                        help="seconds to wait between questions (free tiers limit requests per minute)")
    args = parser.parse_args()

    with QUESTIONS.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.only:
        rows = [r for r in rows if r["id"] in set(args.only)]

    results = []
    for i, r in enumerate(rows):
        if i:
            time.sleep(args.pause)
        print(f"[{r['id']}] {r['question'][:60]}")
        messages = [{"role": "user", "content": redact(r["question"])}]
        answer = None
        for attempt in range(3):
            try:
                answer = get_answer(build_system_prompt(r["reply_lang"]), messages)
                break
            except Exception as e:
                answer = f"ERROR: {e!r}"
                if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                    print("     free-tier limit reached; waiting 60 seconds and trying again...")
                    time.sleep(60)
                else:
                    break
        checks = auto_checks(r["category"], answer)
        print(f"     -> {checks['auto_flags']}")
        results.append({**r, "answer": answer, **checks, **{c: "" for c in MANUAL_COLUMNS}})

    out = ROOT / "eval" / f"results_{datetime.now():%Y%m%d_%H%M}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:  # utf-8-sig so Excel shows Tamil/Bengali
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    flagged = sum(1 for x in results if x["auto_flags"] != "OK")
    print(f"\nDone: {len(results)} questions, {flagged} flagged by auto-checks.")
    print(f"Saved to {out}. Now read every answer and fill in the empty columns.")


if __name__ == "__main__":
    main()
