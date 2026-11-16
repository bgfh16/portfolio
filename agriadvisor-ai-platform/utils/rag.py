"""Builds and searches the AgriAdvisor knowledge base index (RAG, step B).

Two jobs:
  1. build_index()  - reads knowledge_base.md, turns every chunk into numbers
                      (embeddings) and saves them in a FAISS index on disk.
  2. search()       - finds the best chunks for a question by combining two
                      searches: one by meaning (embeddings) and one by exact
                      words (keywords). This is called hybrid search.

The embedding model runs inside the app (fastembed), so it works on your
computer and on Streamlit Cloud without Ollama.

Run from the project folder:
    python utils/rag.py build
    python utils/rag.py ask "How do I control fall armyworm?"
"""

import math
import re
import sys
from itertools import zip_longest
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

sys.path.insert(0, str(Path(__file__).resolve().parent))
from knowledge_loader import load_chunks

# The one setting to change if you ever swap the embedding model.
# After changing it, rebuild the index:  python utils/rag.py build
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
INDEX_FOLDER = Path(__file__).resolve().parent.parent / "data" / "faiss_index"
MODEL_NOTE = INDEX_FOLDER / "embedding_model.txt"   # remembers which model built the index
TOP_K = 6                                  # how many chunks to fetch per question
GUIDE_MAX = 10                             # most chunks returned when a question is about one whole guide


class FastEmbedEmbeddings(Embeddings):
    """Runs a small embedding model inside the app using fastembed.
    The first run downloads the model once (about 130 MB) and keeps it.
    Nomic models work best when text is labelled: 'search_document: ' for
    knowledge base text and 'search_query: ' for questions."""

    def __init__(self, model_name=EMBEDDING_MODEL):
        from fastembed import TextEmbedding
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name)
        self.uses_labels = "nomic" in model_name.lower()

    def _embed(self, texts):
        return [vector.tolist() for vector in self.model.embed(texts)]

    def embed_documents(self, texts):
        if self.uses_labels:
            texts = ["search_document: " + t for t in texts]
        return self._embed(texts)

    def embed_query(self, text):
        if self.uses_labels:
            text = "search_query: " + text
        return self._embed([text])[0]


# ---------- build and load the index ----------

def build_index(embeddings=None):
    """Reads the knowledge base, embeds every chunk and saves the FAISS index."""
    embeddings = embeddings or FastEmbedEmbeddings()
    chunks = load_chunks()
    documents = []
    for chunk in chunks:
        metadata = dict(chunk.metadata)
        metadata["chunk_id"] = chunk.chunk_id
        documents.append(Document(page_content=chunk.text, metadata=metadata))
    print(f"Embedding {len(documents)} chunks with {EMBEDDING_MODEL} ...")
    # normalize_L2 puts every vector on the same scale. Use the same setting
    # when loading (see load_index).
    index = FAISS.from_documents(documents, embeddings, normalize_L2=True)
    INDEX_FOLDER.mkdir(parents=True, exist_ok=True)
    index.save_local(str(INDEX_FOLDER))
    MODEL_NOTE.write_text(EMBEDDING_MODEL, encoding="utf-8")
    print(f"Saved the index to {INDEX_FOLDER}")
    return index


def load_index(embeddings=None):
    """Loads the saved index. Stops with a clear message if it is missing or
    was built with a different embedding model."""
    if not (INDEX_FOLDER / "index.faiss").exists():
        raise FileNotFoundError(
            "The search index has not been built yet. Run: python utils/rag.py build")
    built_with = MODEL_NOTE.read_text(encoding="utf-8").strip() if MODEL_NOTE.exists() else None
    if built_with != EMBEDDING_MODEL:
        raise RuntimeError(
            f"The index was built with '{built_with}' but the app is set to "
            f"'{EMBEDDING_MODEL}'. Rebuild it: python utils/rag.py build")
    embeddings = embeddings or FastEmbedEmbeddings()
    return FAISS.load_local(str(INDEX_FOLDER), embeddings,
                            allow_dangerous_deserialization=True, normalize_L2=True)


# ---------- keyword search ----------

STOP_WORDS = set("a an and are as at be by can do does for from how i in is it my of on or "
                 "should so than that the their this to was what when where which who why "
                 "will with you your me we".split())
SPELLING = {"fertilizer": "fertiliser", "fertilizers": "fertilisers", "harbor": "harbour"}


def _words(text):
    """Lower-cases text and cuts it into simple words, without common filler
    words, and with plural 's' removed so 'tomatoes' and 'tomato' match."""
    words = []
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        word = SPELLING.get(word, word)
        if word in STOP_WORDS:
            continue
        if len(word) > 5 and word.endswith("oes"):      # tomatoes -> tomato, potatoes -> potato
            word = word[:-2]
        elif len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]
        # 'growing' -> 'grow', so a question with 'grow' matches 'Growing Maize'.
        if len(word) > 5 and word.endswith("ing"):
            word = word[:-3]
        words.append(word)
    return words


class KeywordIndex:
    """BM25: scores each chunk by how many of the question's words it contains,
    giving more weight to rare words (like 'pineapple') than to common ones."""

    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.docs = [_words(text) for text in texts]
        self.count = len(self.docs)
        self.average_length = sum(len(d) for d in self.docs) / self.count
        self.document_frequency = {}
        for doc in self.docs:
            for word in set(doc):
                self.document_frequency[word] = self.document_frequency.get(word, 0) + 1

    def scores(self, question):
        question_words = set(_words(question))
        result = []
        for doc in self.docs:
            score = 0.0
            for word in question_words:
                frequency = doc.count(word)
                if not frequency:
                    continue
                df = self.document_frequency[word]
                rarity = math.log(1 + (self.count - df + 0.5) / (df + 0.5))
                length_effect = 1 - self.b + self.b * len(doc) / self.average_length
                score += rarity * frequency * (self.k1 + 1) / (frequency + self.k1 * length_effect)
            result.append(score)
        return result


HEADING_BOOST = 3   # how many extra times the title and section name count in keyword search
_keyword_indexes = {}


def _keyword_index_for(index):
    """Builds the keyword index once from the chunks held in the FAISS index."""
    if id(index) not in _keyword_indexes:
        documents = [index.docstore.search(doc_id) for doc_id in index.index_to_docstore_id.values()]
        # The first line of every chunk is "Title - Section". It is repeated so that a
        # question like "maize fertiliser" matches "Growing Maize - Fertiliser" strongly.
        texts = [(d.page_content.split("\n", 1)[0] + " ") * HEADING_BOOST + d.page_content
                 for d in documents]
        _keyword_indexes[id(index)] = (documents, KeywordIndex(texts))
    return _keyword_indexes[id(index)]


# ---------- hybrid search ----------

def search(question, index=None, k=TOP_K):
    """Returns the k best chunks as a list of (document, closeness) pairs.
    Closeness is the meaning-search score, from about 0 (unrelated) to 1 (same meaning).
    The chunks come from two lists taken in turn: the best keyword match, the best
    meaning match, the second-best keyword match, and so on, skipping repeats."""
    index = index or load_index()
    documents, keyword_index = _keyword_index_for(index)

    # 1. Search by meaning: score every chunk (there are only a few hundred).
    by_meaning = index.similarity_search_with_score(question, k=len(documents))
    closeness = {}
    meaning_order = []
    for doc, distance in by_meaning:
        chunk_id = doc.metadata["chunk_id"]
        closeness[chunk_id] = round(1 - (distance ** 2) / 2, 3)
        meaning_order.append(chunk_id)

    # 2. Search by keywords: only chunks that share at least one word count.
    keyword_scores = keyword_index.scores(question)
    keyword_order = [documents[i].metadata["chunk_id"]
                     for i in sorted((i for i, s in enumerate(keyword_scores) if s > 0),
                                     key=lambda i: -keyword_scores[i])]

    by_id = {d.metadata["chunk_id"]: d for d in documents}

    # 3. Whole-guide rule: if the three best keyword matches all come from one
    #    crop or pest guide, the question is about that topic as a whole (for example
    #    "How do I grow maize?"), so start with that guide's chunks in reading order.
    chosen = []
    top_three = keyword_order[:3]
    if (len(top_three) == 3
            and len({by_id[c].metadata["doc_id"] for c in top_three}) == 1
            and by_id[top_three[0]].metadata["category"] in ("crops", "pests-and-diseases")):
        doc_id = by_id[top_three[0]].metadata["doc_id"]
        chosen = [d.metadata["chunk_id"] for d in documents
                  if d.metadata["doc_id"] == doc_id][:GUIDE_MAX]

    # 4. Then fill up to k chunks by taking from both lists in turn.
    if len(chosen) < k:
        for pair in zip_longest(keyword_order, meaning_order):
            for chunk_id in pair:
                if chunk_id and chunk_id not in chosen:
                    chosen.append(chunk_id)
            if len(chosen) >= k:
                break
        chosen = chosen[:k]

    return [(by_id[c], closeness[c]) for c in chosen]


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build_index()
    elif len(sys.argv) >= 3 and sys.argv[1] == "ask":
        for doc, closeness in search(" ".join(sys.argv[2:])):
            print(f"{closeness:.3f}  {doc.metadata['chunk_id']}")
            print("       " + doc.page_content.replace("\n", " ")[:160] + "...")
    else:
        print('Use:  python utils/rag.py build    or    python utils/rag.py ask "your question"')
