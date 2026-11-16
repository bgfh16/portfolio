"""One place for every call to the AI (step 14).

The pages call ask(messages, purpose) and get the reply text back. They do not need
to know whether Ollama (on your own computer) or Groq (online) is behind it.

Settings:
  - AI_PROVIDER in .streamlit/secrets.toml: "groq" (default) or "ollama".
  - GROQ_API_KEY in .streamlit/secrets.toml (only needed for Groq).
  - The model names below. If Groq retires a model, change its name here, nowhere else.

Run a quick check from the project folder:
    python utils/llm.py                          (text check)
    python utils/llm.py image "photos/crop.jpg"   (photo check)
"""
import base64
import io
import re

import streamlit as st

# ---------- settings you may need to change ----------

# For each purpose, the Groq models to try in order. If the first one is busy,
# out of its daily allowance, or retired, the next one is tried.
GROQ_MODELS = {
    "chat":      ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"],
    "recommend": ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"],
    "title":     ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"],
    "vision":    ["qwen/qwen3.8-27b"],     # the only model here that reads photos
}

# The model used when AI_PROVIDER is "ollama" (your own computer).
OLLAMA_MODELS = {
    "chat": "llama3.2",
    "recommend": "llama3.2",
    "title": "llama3.2",
    "vision": "llava",
}

# Photos are shrunk before they are sent, so large uploads stay within Groq's request
# size limit and use fewer tokens. 1280 pixels on the long side is plenty to see leaves.
IMAGE_MAX_SIDE = 1280
IMAGE_JPEG_QUALITY = 85

GROQ_TIMEOUT_SECONDS = 30


class AIUnavailableError(Exception):
    """Raised when no model could answer. The page catches it and shows its friendly message."""


def _secret(name, default=None):
    """Reads one value from secrets.toml, or returns the default if it is missing."""
    try:
        return st.secrets[name]
    except Exception:
        return default


# ---------- Groq ----------

_groq_client = None


def _get_groq_client():
    """Creates the Groq connection once and reuses it."""
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        key = _secret("GROQ_API_KEY")
        if not key:
            raise AIUnavailableError("GROQ_API_KEY is missing from .streamlit/secrets.toml")
        # max_retries=0: if a model is busy we move to the next model straight away
        # instead of waiting and retrying the same one.
        _groq_client = Groq(api_key=key, timeout=GROQ_TIMEOUT_SECONDS, max_retries=0)
    return _groq_client


def _clean(text):
    """Removes any <think>...</think> block that a model may put before its answer."""
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.DOTALL).strip()


def _ask_groq(messages, purpose, temperature):
    client = _get_groq_client()
    last_error = None
    for model in GROQ_MODELS[purpose]:
        settings = {"model": model, "messages": messages, "temperature": temperature}
        # The gpt-oss models "think" before answering, which uses up tokens.
        # "low" keeps that short so more questions fit in the daily allowance.
        if model.startswith("openai/gpt-oss"):
            settings["reasoning_effort"] = "low"
        try:
            try:
                response = client.chat.completions.create(**settings)
            except Exception as error:
                # If this model does not accept the reasoning setting, try once without it.
                if "reasoning_effort" in settings and "reasoning" in str(error).lower():
                    del settings["reasoning_effort"]
                    response = client.chat.completions.create(**settings)
                else:
                    raise
            text = _clean(response.choices[0].message.content)
            if text:
                # Shown in the terminal only, so you can watch your token use.
                print(f"[AI] {model} ({purpose}) used {response.usage.total_tokens} tokens")
                return text
            print(f"[AI] {model} ({purpose}) gave an empty answer, trying the next model")
        except Exception as error:
            last_error = error
            print(f"[AI] {model} ({purpose}) failed: {type(error).__name__}, trying the next model")
    raise AIUnavailableError(f"No Groq model could answer ({purpose}). Last error: {last_error}")


# ---------- Ollama ----------

def _ask_ollama(messages, purpose, temperature):
    import ollama
    try:
        response = ollama.chat(
            model=OLLAMA_MODELS[purpose],
            messages=messages,
            options={"temperature": temperature, "num_ctx": 4096},
        )
        return response["message"]["content"]
    except Exception as error:
        raise AIUnavailableError(f"Ollama could not answer ({purpose}): {error}") from error


# ---------- the one function the pages use ----------

def ask(messages, purpose, temperature=0.2):
    """Sends the messages to the AI and returns its reply as text.

    messages: a list like [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    purpose:  "chat", "recommend" or "title" (decides which model is used)
    Raises AIUnavailableError if no model could answer.
    """
    if _secret("AI_PROVIDER", "groq") == "ollama":
        return _ask_ollama(messages, purpose, temperature)
    return _ask_groq(messages, purpose, temperature)


def _prepare_image(image_bytes):
    """Shrinks a photo and returns it as JPEG bytes."""
    from PIL import Image
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    image.thumbnail((IMAGE_MAX_SIDE, IMAGE_MAX_SIDE))
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=IMAGE_JPEG_QUALITY)
    return output.getvalue()


def ask_with_image(prompt, image_bytes, temperature=0.2):
    """Sends a photo and a question to the AI and returns its reply as text.

    prompt:      the instructions, as text
    image_bytes: the photo file's bytes (JPG or PNG)
    Raises AIUnavailableError if no model could answer.
    """
    try:
        jpeg = _prepare_image(image_bytes)
    except Exception as error:
        raise AIUnavailableError(f"The photo could not be read: {error}") from error

    if _secret("AI_PROVIDER", "groq") == "ollama":
        messages = [{"role": "user", "content": prompt, "images": [jpeg]}]
        return _ask_ollama(messages, "vision", temperature)

    data_url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ],
    }]
    return _ask_groq(messages, "vision", temperature)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "image":
        photo = open(sys.argv[2], "rb").read()
        print(ask_with_image("Describe what you see in this photo in two sentences. "
                             "Say whether it shows a plant, crop or farm produce.", photo))
        sys.exit()
    for purpose in ("chat", "recommend", "title"):
        print("=" * 50)
        print("Purpose:", purpose)
        try:
            print(ask([{"role": "user", "content": "In one sentence, why do farmers mulch their crops?"}], purpose))
        except AIUnavailableError as error:
            print("FAILED:", error)
