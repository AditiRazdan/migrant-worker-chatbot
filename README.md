# Catalyst Bot

A mobile chat that answers migrant workers' questions about salary, work rules, safety and
healthcare, **only** from the verified resource sheet, in Tamil, Bengali or English.

## What's in this folder

| File | What it does | Will you edit it? |
|---|---|---|
| `knowledge/resource_sheet.md` | All the facts + official links. The bot knows nothing else. | Yes, whenever rules change |
| `prompts.py` | The bot's rules (only use the sheet, always cite, 995 first, no personal data…) | Sometimes, after testing |
| `ui_text.py` | Fixed screen text in 3 languages (emergency banner, welcome, errors) | **Get Tamil/Bengali checked** |
| `app.py` | The chat screen | Rarely |
| `llm.py` | Talks to the AI model (Groq, Gemini or Claude) | No; choose provider in secrets |
| `list_gemini_models.py` | Lists Gemini models your key can use | No |
| `chatlog.py` | Anonymous logging + removes FIN/phone numbers/emails | Rarely |
| `eval/test_questions.csv` | 30 test questions | Yes, add more |
| `eval/run_tests.py` | Runs all test questions, makes a scoring sheet | No |

## How it works (for your presentation)

```
Worker's phone ──► picks language ──► types question (any language / romanised / misspelled)
                                              │
                         privacy filter removes FIN, phone numbers, emails
                                              │
          AI model gets: RULES + WHOLE RESOURCE SHEET + recent conversation
                                              │
          answer in worker's language + official source link (or "I don't know" + MWC)
                                              │
                    anonymous log (question, answer, 👍/👎, dorm A/B)
```
No vector database needed: the sheet is small enough to send in full every time, so the bot
always sees every fact. The emergency banner is fixed text, so it never depends on the AI.

---

## Step 1 · Run it on your laptop

1. Install Python 3.10 or newer.
2. In a terminal, inside this folder:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Step 2 · Add your API key

The bot works with **Groq** (free tier, no card; the default), **Gemini** (Google, free tier) or
**Claude** (Anthropic, paid credits). Choose with one line in your secrets file:
`PROVIDER = "groq"`, `"gemini"` or `"claude"`.

1. Get a key:
   - Groq: console.groq.com → sign up → **API Keys** → Create API Key.
   - Gemini: Google AI Studio → **Get API key** → Create API key.
   - Claude: Claude Console (platform.claude.com) → buy credits → API Keys → Create key.
2. `.streamlit/secrets.toml` is already in the folder (the `.streamlit` folder is hidden; press
   Cmd+Shift+. in Finder to see it). Open it from Terminal with `open -e .streamlit/secrets.toml`,
   replace `PASTE-KEY-HERE` with your key, keeping the quote marks, and save.
3. Never put the key in code, chats, screenshots or GitHub (`.gitignore` already blocks
   `secrets.toml`). If a key ever leaks, delete it and make a new one.

**Groq free tier, limits:** the free plan has per-minute and per-day limits that are shared by
everyone using your bot (see console.groq.com → Settings → Limits). The default model,
`openai/gpt-oss-120b`, caches the resource sheet so it barely counts toward those limits after the
first question. If workers see the "something went wrong" message during the pilot, check the
terminal for `429`: that means the limit was hit, and it resets after a minute or the next day.
Groq runs open-source models, so check the Tamil and Bengali answers carefully in Step 4.

**Gemini free tier, privacy:** Google may use free-tier questions and answers to improve its
products, and human reviewers may read them. That's fine for your own testing. Before real
workers use it, either turn on billing (then Google doesn't use the data) or add a clear notice in
their language and get Ms. Wang's OK.

**Model errors?** If Gemini says the model isn't found, run `python list_gemini_models.py` and put
one of the "flash" models it lists into secrets as `MODEL = "..."`.

## Step 3 · Start the app

```bash
streamlit run app.py
```
It opens at http://localhost:8501. To try it on your phone, use the "Network URL" it prints
(phone and laptop on the same Wi-Fi).

## Step 4 · Test before any worker sees it

```bash
python eval/run_tests.py
```
It pauses 8 seconds between questions, and if a free-tier limit is hit it waits a minute and tries again. It asks all 30 test questions and saves `eval/results_<date>.csv`. Open it in Google Sheets.

- **auto_flags** catches obvious problems: a link or phone number that isn't in your sheet
  (= the AI made it up), a missing source, no contact on an "I don't know", or 995 not first in
  an emergency.
- Then read every answer and fill in the empty columns yourself. Ask a Tamil speaker and a
  Bengali speaker to fill **translation_ok** for their language.
- Fix problems by editing `prompts.py` (rules) or `resource_sheet.md` (facts), then run again.
  Keep each results file: before-and-after scores are great evidence for your journal.

Run only some questions: `python eval/run_tests.py --only 13 24 29`

## Step 5 · Put it online (free)

1. Put this folder in a GitHub repo (private is fine; Streamlit's free plan allows one private app).
2. Go to share.streamlit.io → sign in with GitHub → **Create app** → pick the repo and `app.py`.
3. Under **Advanced settings → Secrets**, paste everything from your `secrets.toml`.
4. Deploy. You get a link like `https://catalyst-bot.streamlit.app`.

**Sleep warning:** free Streamlit apps go to sleep after 12 hours with no visitors, and the next
person sees a "wake up" button. During the pilot, open the link yourself each morning.

## Step 6 · Save logs to a Google Sheet (do this before the pilot)

The free hosting **deletes local files** whenever the app restarts or sleeps, so
`logs/chat_log.csv` won't survive online. Send logs to a Google Sheet instead:

1. Go to console.cloud.google.com → create a project (use a personal Google account; school
   accounts often block this).
2. **APIs & Services → Library**: enable **Google Sheets API** and **Google Drive API**.
3. **IAM & Admin → Service Accounts → Create**. Open it → **Keys → Add key → JSON**. A file downloads.
4. Create an empty Google Sheet. Click **Share** and add the service account's email
   (from the JSON, `client_email`) as **Editor**.
5. In your Streamlit secrets, add `LOG_SHEET_URL` and the `[gcp_service_account]` section
   (copy each field from the JSON file; see `secrets.toml.example`).
6. Ask the bot one question, then check that a row appears in the sheet.

## Step 7 · Pilot links for the two dorms

Give each dorm its own link so you can compare them in the logs:

- Dorm A: `https://<your-app>.streamlit.app/?dorm=A`
- Dorm B: `https://<your-app>.streamlit.app/?dorm=B`

Make a QR code for each (any free QR generator) for the posters, and send the links through
the dorm managers' WhatsApp groups.

## Before launch checklist

- [ ] Native speakers checked every line in `ui_text.py` (Tamil and Bengali)
- [ ] All links in `resource_sheet.md` re-checked; "Last checked" date updated
- [ ] Full test run: no "link not in sheet" / "number not in sheet" flags, and all emergency questions show 995 first
- [ ] Ms. Wang has tried it and reviewed the safeguards
- [ ] Google Sheet logging works on the online version
- [ ] You've opened both dorm links on a phone

## Updating facts later

Edit only `knowledge/resource_sheet.md`. Keep the same layout (question / Answer / Source with
the full link), update the "Last checked" date, and run the tests again. Remember the Primary Care
Plan changes on 1 April 2027.
