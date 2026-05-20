# Harry Potter Script Generator

An AI-powered movie screenplay generator that scrapes real Harry Potter lore from the web and uses it as context to write an original, cinematic script in the style of the Harry Potter universe. Built with Python, Jupyter Notebook, and a locally running LLM via Ollama.

---

## Overview

This project combines web scraping and local LLM inference to produce something creative: a brand new Harry Potter screenplay grounded in actual canon lore. Rather than relying purely on what the model already knows, it first scrapes up-to-date content from Wikipedia and the Harry Potter fandom wiki, injects that context into the prompt, and then asks the model to write an original script around unresolved mysteries, forgotten magic, or unexplored characters.

The output streams directly into the notebook as formatted Markdown, rendered in proper screenplay style — scene headings, dialogue blocks, and all.

---

## How It Works

**Step 1 — Scrape the lore**

`scraper.py` handles all web fetching. It sends a browser-like request to each URL, parses the HTML with BeautifulSoup, strips out irrelevant elements (scripts, styles, images), and returns a clean block of text truncated to 2,000 characters. It also normalises known problematic URLs before making any request, so scraping doesn't silently fail on bad domains.

Two pages are scraped:
- `https://en.wikipedia.org/wiki/Harry_Potter` — general background and plot overview
- `https://harrypotter.fandom.com/wiki/Hogwarts` — detailed Hogwarts lore

Both are combined into a single context string.

**Step 2 — Build the prompt**

The system prompt tells the model it is an expert fantasy screenplay writer and gives it strict formatting rules: use proper scene headings (`INT. HOGWARTS - NIGHT`), write dialogue with character names centred above their lines, keep the tone magical and immersive, and return clean Markdown with no code blocks.

The user prompt includes a one-shot example of the expected screenplay format, followed by the full scraped lore. This gives the model both a structural template and real factual grounding to work from.

**Step 3 — Stream the output**

The model response is streamed chunk by chunk and progressively rendered as Markdown in the notebook using `update_display`. This means you see the screenplay being written in real time rather than waiting for the full response.

---

## Project Structure

```
harry-potter-script-generator/
│
├── README.md                             # Project documentation
├── harry-potter-script-generator.ipynb   # Main notebook 
├── requirements.txt                      # Python dependencies
└── scraper.py                            # Web scraping utilities
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
   jupyter notebook harry-potter-script-generator.ipynb
   ```
5. Run all cells. The script will scrape the lore, build the prompt, and stream the generated screenplay directly into the notebook output.

---

## Key Components

### `scraper.py`

Contains three functions:

- `_normalize_url(url)` — an internal helper that fixes known problematic URLs before any request is made. Prefixed with `_` by convention to signal it's an implementation detail, not meant to be called externally.
- `fetch_website_contents(url)` — fetches a page, strips irrelevant HTML elements, and returns the title plus body text (capped at 2,000 characters).
- `fetch_website_links(url)` — fetches all `<a href>` links from a page and returns them as a list. (This wasn't made use of in the main notebook).

### `harry-potter-script-generator.ipynb`

- Sets up the Ollama client using the OpenAI SDK pointed at the local endpoint.
- Defines the system and user prompts.
- Calls the scraper to build lore context.
- Streams the model's screenplay response into the notebook with live Markdown rendering.

---

## Example Output

```
# Harry Potter and the Lost Heir

## Opening Scene

INT. MINISTRY OF MAGIC - NIGHT

Hermione Granger, now in her 30s, studies an ancient scroll under dim lamplight.

                    HERMIONE
        This can't be... It's too late...

A knock breaks the silence. Minister Fawkes stands in the doorway.

                    MINISTER FAWKES
        There's something new that requires your expertise.
```

---

## Customisation

- **Change the model** — swap `llama3.2` in the `MODEL` variable for any other Ollama model (e.g. `mistral`, `gemma3`, `phi4`).
- **Add more lore sources** — extend `get_harry_potter_lore()` with additional `fetch_website_contents()` calls to feed the model richer context.
- **Change the story direction** — edit the user prompt to steer the screenplay toward a specific character, era, or mystery (e.g. the Marauders era, the founding of Hogwarts).
- **Save the output** — capture the final `response` string and write it to a `.md` file for a clean, exportable screenplay.

---

## Notes

This project uses Ollama's OpenAI-compatible API endpoint (`http://localhost:11434/v1`). The `api_key` is set to the placeholder string `'ollama'` — this is just to satisfy the OpenAI SDK's interface requirement; no real API key is involved.
```
