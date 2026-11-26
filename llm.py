"""Everything that talks to the AI model lives here.

Pick the AI provider in .streamlit/secrets.toml:
    PROVIDER = "groq"     -> uses GROQ_API_KEY     (Groq; free tier, no card)
    PROVIDER = "gemini"   -> uses GEMINI_API_KEY   (Google; has a free tier)
    PROVIDER = "claude"   -> uses ANTHROPIC_API_KEY (Anthropic; paid credits)
The rest of the app doesn't change.
"""

import os
from pathlib import Path

MAX_ANSWER_TOKENS = 1500  # room for the model's thinking + a short answer

DEFAULT_MODELS = {
    "claude": "claude-haiku-5-5",
    # Groq's GPT-OSS 120B caches the resource sheet automatically, and cached tokens
    # don't count toward the free-tier limits.
    "groq": "openai/gpt-oss-120b",
    # "gemini-flash-latest" always points to Google's newest Flash model.
    # If it gives an error, run `python list_gemini_models.py` and pick one from the list.
    "gemini": "gemini-flash-latest",
}


def _get_secret(name, default=None):
    """Read a setting from Streamlit secrets, falling back to environment variables."""
    try:
        import streamlit as st

        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


def provider():
    return str(_get_secret("PROVIDER", "groq")).strip().lower()


def _require_key(name):
    """Get an API key, or explain clearly what's wrong with the secrets file."""
    key = _get_secret(name)
    secrets_file = Path.cwd() / ".streamlit" / "secrets.toml"
    if not secrets_file.exists() and not key:
        raise RuntimeError(
            f"No secrets file at {secrets_file}. Run 'streamlit run app.py' from inside the "
            "catalyst-bot folder, and check .streamlit/secrets.toml exists."
        )
    if not key:
        raise RuntimeError(f'{name} is not in {secrets_file}. Add the line: {name} = "your-key"')
    if "PASTE" in key:
        raise RuntimeError(f"You haven't pasted your key yet: replace PASTE-KEY-HERE in {secrets_file}")
    return key


def _model():
    return _get_secret("MODEL", DEFAULT_MODELS[provider()])


# ---------------- Claude (Anthropic) ----------------

def _claude_client():
    import anthropic

    return anthropic.Anthropic(api_key=_require_key("ANTHROPIC_API_KEY"))


def _claude_request(system_prompt, messages):
    return dict(
        model=_model(),
        max_tokens=MAX_ANSWER_TOKENS,
        # Note: Claude Haiku 5.5 rejects temperature/top_p/top_k, so don't add them.
        # The resource sheet is the same on every request, so cache it (cheaper + faster).
        system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    )


# ---------------- Gemini (Google) ----------------

def _gemini_client():
    from google import genai

    return genai.Client(api_key=_require_key("GEMINI_API_KEY"))


def _gemini_request(system_prompt, messages):
    from google.genai import types

    # Gemini calls the assistant "model" and wraps text in "parts".
    contents = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=MAX_ANSWER_TOKENS,
    )
    return dict(model=_model(), contents=contents, config=config)


# ---------------- Groq ----------------

def _groq_client():
    from groq import Groq

    return Groq(api_key=_require_key("GROQ_API_KEY"))


def _groq_request(system_prompt, messages):
    request = dict(
        model=_model(),
        # The system prompt goes first and never changes, so Groq can cache it.
        messages=[{"role": "system", "content": system_prompt}, *messages],
        max_completion_tokens=MAX_ANSWER_TOKENS,
    )
    if request["model"].startswith("openai/gpt-oss"):
        # "medium" reads the sheet more carefully; "low" uses fewer free-limit tokens.
        request["reasoning_effort"] = _get_secret("REASONING_EFFORT", "medium")
    return request


# ---------------- Used by the app and the tests ----------------

def stream_answer(system_prompt, messages):
    """Yield the answer piece by piece, so the worker sees it appear as it is written."""
    if provider() == "groq":
        for chunk in _groq_client().chat.completions.create(**_groq_request(system_prompt, messages), stream=True):
            text = chunk.choices[0].delta.content if chunk.choices else None
            if text:
                yield text
    elif provider() == "gemini":
        for chunk in _gemini_client().models.generate_content_stream(**_gemini_request(system_prompt, messages)):
            if chunk.text:
                yield chunk.text
    else:
        with _claude_client().messages.stream(**_claude_request(system_prompt, messages)) as stream:
            for text in stream.text_stream:
                yield text


def get_answer(system_prompt, messages):
    """Return the whole answer at once (used by the test runner)."""
    if provider() == "groq":
        response = _groq_client().chat.completions.create(**_groq_request(system_prompt, messages))
        return response.choices[0].message.content or ""
    if provider() == "gemini":
        response = _gemini_client().models.generate_content(**_gemini_request(system_prompt, messages))
        return response.text or ""
    response = _claude_client().messages.create(**_claude_request(system_prompt, messages))
    return "".join(block.text for block in response.content if block.type == "text")
