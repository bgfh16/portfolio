# AgriAdvisor

AgriAdvisor is a web app that gives small-scale farmers in Nigeria practical farming advice. Farmers can ask questions in a chat, upload a photo of a crop to get a diagnosis, get crop suggestions for their state and season, and browse a pest and disease guide. Answers are grounded in a curated Nigerian farming knowledge base. This app was built as my final-year project.

**Module:** SWE6010 Undergraduate Project

**Student:** Daniel Agbonmeire Oyakhire

**Programme:** BEng (Hons) Software Engineering Top-Up, University of Greater Manchester

## Features

- **Chat**: ask farming questions and get answers based on the knowledge base. Conversations are saved, titled automatically and can be continued later.
- **History**: browse, reopen and delete past conversations.
- **Image Diagnosis**: upload a photo of a crop to get a structured diagnosis (crop, problem, causes, remedies), then ask follow-up questions. Diagnoses and their photos are saved and can be reopened or deleted.
- **Crop Recommendations**: choose a crop type, a state and a season to get 3 to 5 suggested crops for that state's agro-ecological zone.
- **Pest and Disease Guide**: reference pages for common crop pests and diseases.
- **Accounts**: sign up, log in, log out, session restore after a page refresh, profile and settings, and account deletion that asks for the account password.
- **Friendly error handling**: if an AI request fails or a limit is reached, the app shows a plain message with a Retry button instead of crashing.

## How the advice is produced

AgriAdvisor uses retrieval-augmented generation (RAG):

1. **Knowledge base**: `data/knowledge_base.md` holds 46 documents on crops, pests and diseases, soil and fertiliser, farm practices, climate, and regions and seasons. It is split by section into 276 chunks.
2. **Embeddings**: each chunk is turned into numbers with the `BAAI/bge-small-en-v1.5` model, run inside the app with `fastembed`, and stored in a FAISS index (`data/faiss_index`).
3. **Hybrid search**: a question is searched in two ways, by meaning (embeddings) and by keywords (BM25, with section headings weighted), and the best chunks from both lists are combined. When a question is about one whole crop or pest guide, the guide's sections are returned in reading order.
4. **Zone lookup**: if a Nigerian state is named, the app adds its agro-ecological zone (from `utils/zones.py`) to the instructions, so the model does not have to guess it.
5. **Answer**: the chunks and the conversation are sent to a language model through Groq. The prompt tells the model to use only the supplied passages, quote figures exactly, never invent prices or numbers, and never give pesticide doses.

Image Diagnosis sends the (resized) photo to a vision model on Groq.

## Tech stack

| Area | Technology |
|---|---|
| App and interface | Streamlit |
| Accounts, database and image storage | Supabase (authentication, Postgres with row-level security, storage) |
| Retrieval | LangChain, FAISS, fastembed, BM25 keyword search |
| Language and vision models | Groq (production); Ollama (optional, local) |
| Hosting | Streamlit Community Cloud |

Models are listed in one place, `utils/llm.py`. Each task (chat, recommendations, titles, vision) has a list of models and falls back to the next one if a model is rate-limited or fails.

## Project structure

```
app.py                  Entry point
views/                  Pages (chat, history, image diagnosis, crop recommendations, etc.)
components/             Shared interface parts such as the sidebar
utils/
  rag.py                Builds and searches the knowledge base index
  knowledge_loader.py   Reads and splits knowledge_base.md into chunks
  llm.py                Groq and Ollama calls, model fallback, image preparation
  zones.py              State-to-zone list and state detection
  rag_check.py          Prints retrieval results for a set of test questions
  supabase_client.py    Supabase connection
data/
  knowledge_base.md     The knowledge base
  faiss_index/          The saved search index
assets/                 Styles and images
.streamlit/secrets.toml Local secrets (not committed)
requirements.txt        Python packages
```

## Running it locally

Requires Python 3.11.

1. Create and activate a virtual environment. On Windows, keep its path short (for example `C:\agriadvisor_venv`), because a very long path stops `onnxruntime` from loading.
   ```
   python -m venv C:\agriadvisor_venv
   C:\agriadvisor_venv\Scripts\activate
   ```
2. Install the packages:
   ```
   pip install -r requirements.txt
   ```
3. Create `.streamlit/secrets.toml` with your own keys (see Configuration below).
4. Build the search index (only needed if `data/faiss_index` is missing or the knowledge base or embedding model changed):
   ```
   python utils/rag.py build
   ```
5. Start the app:
   ```
   streamlit run app.py
   ```

The first run downloads the embedding model (about 67 MB) once.

### Useful commands

```
python utils/rag.py ask "How do I control fall armyworm?"   # see which chunks a question finds
python utils/rag_check.py                                   # run the retrieval check questions
python utils/llm.py                                         # test the Groq connection
python utils/llm.py image "photos/crop.jpg"                 # test the vision model
```

## Configuration

Secrets live in `.streamlit/secrets.toml` locally and in the app settings on Streamlit Community Cloud. They are never committed.

| Secret | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq API key |
| `AI_PROVIDER` | Optional. `groq` (default) or `ollama` to use a local model |
| Supabase URL and key | Connection to the Supabase project |

To use Ollama locally, install Ollama, pull the models named in `utils/llm.py`, and set `AI_PROVIDER = "ollama"`.

## Deployment

The app deploys from a GitHub repository to Streamlit Community Cloud (Python 3.11). Commit `data/faiss_index` with the app so the server does not have to rebuild it. Add the secrets in the app's settings. The embedding model is downloaded on the first search after the server starts.

## Known limitations

- The free Groq plan has tight per-model rate and daily token limits, so heavy use can trigger the "try again" message.
- Language models can still make small mistakes with figures or places even when given the right passages, and the vision model can give different answers to the same photo on different runs.
- The knowledge base does not cover every Nigerian crop (for example sugarcane or ginger), and it has no season-specific planting detail or prices. For these, the app says it has no specific guidance and suggests an agricultural extension officer.
- Image Diagnosis is not grounded in the knowledge base.
- There is no password reset, because Supabase reset links cannot reach a Streamlit app.
- AgriAdvisor gives general guidance only. Farmers should follow product labels and ask a local agricultural extension officer, especially before using any chemical.
