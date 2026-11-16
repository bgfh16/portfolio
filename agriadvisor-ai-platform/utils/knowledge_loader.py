"""Loads knowledge_base.md and cuts it into chunks for the RAG search.

The file holds many documents separated by <<<DOCUMENT>>>. Each document starts
with a header (title, category, sources, ...) between two --- lines, followed by
a # title and ## sections. One chunk is made per ## section, and every chunk
keeps its document's title, category and other details as metadata.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

DOCUMENT_MARKER = "<<<DOCUMENT>>>"
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base.md"
MIN_SECTION_WORDS = 15   # shorter sections are joined to the next one, because a few words search badly


@dataclass
class Chunk:
    chunk_id: str
    text: str                      # what gets searched and sent to the AI
    metadata: dict = field(default_factory=dict)


def _clean_value(value):
    """Turns '[a, b, c]' into a list, and removes quotes around plain text."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
    return value.strip('"')


def _parse_header(header_text):
    """Reads the simple key: value header at the top of each document."""
    meta = {}
    current_list_key = None
    for line in header_text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key:
            meta[current_list_key].append(line[4:].strip().strip('"'))
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if value.strip() == "":
            meta[key] = []
            current_list_key = key
        else:
            meta[key] = _clean_value(value)
            current_list_key = None
    return meta


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _split_sections(body):
    """Splits a document body into (heading, text) pairs on '## ' headings.
    Text before the first '## ' heading becomes an 'Overview' section."""
    parts = re.split(r"^## ", body, flags=re.MULTILINE)
    sections = []
    intro = parts[0]
    # drop the '# Title' line from the intro
    intro = re.sub(r"^# .*\n?", "", intro, count=1, flags=re.MULTILINE).strip()
    if intro:
        sections.append(("Overview", intro))
    for part in parts[1:]:
        heading, _, text = part.partition("\n")
        text = text.strip()
        if text:
            sections.append((heading.strip(), text))
    return _merge_tiny_sections(sections)


def _merge_tiny_sections(sections):
    """Joins a very short section (for example 'Affects: Cassava. Severity: High.')
    to the section after it, or to the one before it if it is the last."""
    merged = []
    carry = ""
    for heading, text in sections:
        if carry:
            text = carry + "\n\n" + text
            carry = ""
        if len(text.split()) < MIN_SECTION_WORDS:
            carry = text if heading == "Overview" else f"{heading}: {text}"
            continue
        merged.append((heading, text))
    if carry:
        if merged:
            heading, text = merged[-1]
            merged[-1] = (heading, text + "\n\n" + carry)
        else:
            merged.append(("Overview", carry))
    return merged


def load_chunks(path=DEFAULT_PATH):
    """Reads the knowledge base file and returns a list of Chunk objects."""
    raw = Path(path).read_text(encoding="utf-8")
    chunks = []
    for document in raw.split(DOCUMENT_MARKER):
        document = document.strip()
        if not document:
            continue
        match = re.match(r"---\n(.*?)\n---\n(.*)", document, flags=re.DOTALL)
        if not match:
            raise ValueError("A document is missing its --- header: " + document[:60])
        meta = _parse_header(match.group(1))
        title = meta.get("title")
        if not title:
            raise ValueError("A document has no title: " + document[:60])
        doc_id = _slug(title)

        for number, (heading, text) in enumerate(_split_sections(match.group(2)), start=1):
            chunks.append(Chunk(
                chunk_id=f"{doc_id}#{number}",
                text=f"{title} - {heading}\n\n{text}",
                metadata={
                    "doc_id": doc_id,
                    "title": title,
                    "section": heading,
                    "category": meta.get("category", ""),
                    "crop_group": meta.get("crop_group", ""),
                    "type": meta.get("type", ""),
                    "crops": meta.get("crops", []),
                    "severity": meta.get("severity", ""),
                    "topics": meta.get("topics", []),
                    "sources": meta.get("sources", []),
                },
            ))
    return chunks


if __name__ == "__main__":
    # Run from the project folder:  python utils/knowledge_loader.py
    all_chunks = load_chunks()
    docs = {c.metadata["doc_id"] for c in all_chunks}
    words = [len(c.text.split()) for c in all_chunks]
    print(f"Documents: {len(docs)}")
    print(f"Chunks:    {len(all_chunks)}")
    print(f"Words per chunk: smallest {min(words)}, largest {max(words)}, "
          f"average {sum(words) // len(words)}")

    by_category = {}
    for c in all_chunks:
        by_category[c.metadata["category"]] = by_category.get(c.metadata["category"], 0) + 1
    print("\nChunks per category:")
    for category, count in sorted(by_category.items()):
        print(f"  {category}: {count}")

    print("\nThree sample chunks:")
    for index in (0, len(all_chunks) // 2, len(all_chunks) - 1):
        chunk = all_chunks[index]
        print("\n" + "-" * 60)
        print("ID:       ", chunk.chunk_id)
        print("Category: ", chunk.metadata["category"])
        print("Section:  ", chunk.metadata["section"])
        print("Sources:  ", len(chunk.metadata["sources"]), "listed")
        print("Text:\n" + chunk.text[:400] + ("..." if len(chunk.text) > 400 else ""))
