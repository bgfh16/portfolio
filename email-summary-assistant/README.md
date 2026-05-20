# Email Summary Assistant

A lightweight AI-powered tool that reads an email and returns a concise summary along with a bullet-point breakdown of its key details. Built with Python and Jupyter Notebook, it runs a local LLM through Ollama using an OpenAI-compatible interface.

---

## Overview

Keeping up with emails can be tedious, especially when a message is long-winded but the important bits could fit in a few lines. This project tackles that by sending an email's content to a locally running language model (`llama3.2` via Ollama) with a carefully crafted system prompt that instructs it to summarize concisely and highlight key details in bullet points.

The output is rendered as formatted Markdown directly inside the notebook, making it easy to read at a glance.

---

## How It Works

1. A system prompt defines the assistant's behaviour — summarize the email, keep it concise, and follow up with bullet points.
2. A user prompt carries the actual email content.
3. Both are packaged into a `messages` list and sent to the Ollama server via the OpenAI Python SDK (pointed at the local Ollama endpoint).
4. The model's response is extracted and rendered as Markdown in the notebook output.

---

## Project Structure

```
email-summary-assistant/
│
├── README.md                       # Project documentation
├── email-summary-assistant.ipynb   # Main notebook
└── requirements.txt                # Python dependencies
```

---

## Prerequisites

- Python 3.10+
- Ollama installed and running locally — https://ollama.com
- The `llama3.2` model pulled into Ollama:
  ```bash
  ollama pull llama3.2
  ```

---

## Setup & Usage

1. Clone or download this repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Make sure Ollama is running:
   ```bash
   ollama serve
   ```
4. Open the notebook:
   ```bash
   jupyter notebook email-summary-assistant.ipynb
   ```
5. Paste the email you want summarized into the `user_prompt` variable in the second cell, then run all cells.

---

## Example Output

Given a casual invitation email, the assistant produces something like:

**Summary:**
Jessica is reaching out after a long time to invite Annie to a gathering this Friday — a relaxed get-together with food, music, and catching up.

**Key Details:**
- Long time since they last caught up
- Invitation to a Friday gathering
- Event includes food, dancing, and sharing stories
- Jessica promises to save Annie a snack

---

## Customization

- **Swap the model** — replace `llama3.2` in the `MODEL` variable with any other model you have pulled in Ollama (e.g. `mistral`, `gemma3`).
- **Adjust the system prompt** — tweak the tone, output format, or level of detail to suit your use case.
- **Automate email input** — integrate with an email client or API to feed emails in dynamically rather than pasting them manually.

---

## Notes

This project uses Ollama's OpenAI-compatible API endpoint (`http://localhost:11434/v1`), which means the OpenAI Python SDK works out of the box without any real API key — the `api_key` is set to the placeholder string `'ollama'` as required by the SDK's interface.
```
