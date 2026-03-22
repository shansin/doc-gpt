import re


# Sentence boundary: split after .!? followed by whitespace
_SENT_RE = re.compile(r'(?<=[.!?])\s+')

# Abbreviations that should not trigger a sentence break
_ABBREVS = frozenset(
    "Mr. Mrs. Ms. Dr. Prof. Sr. Jr. St. vs. etc. Inc. Ltd. Corp. Co. "
    "U.S. e.g. i.g. i.e. al. No. Vol. Fig. Ch. Sec. Gov. Gen.".split()
)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, merging back false splits on abbreviations."""
    raw = _SENT_RE.split(text)
    if not raw:
        return []

    merged: list[str] = [raw[0]]
    for part in raw[1:]:
        prev = merged[-1]
        # Check if previous fragment ends with a known abbreviation or a digit
        # followed by a period (e.g. "3.") — if so, rejoin instead of splitting
        last_word = prev.rsplit(None, 1)[-1] if prev else ""
        if last_word in _ABBREVS or re.match(r'\d+\.$', last_word):
            merged[-1] = prev + " " + part
        else:
            merged.append(part)

    return [p for p in merged if p.strip()]


def _is_table_line(line: str) -> bool:
    """Check if a line is part of a markdown table."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def _is_table_separator(line: str) -> bool:
    """Check if a line is a markdown table separator (|---|---|)."""
    stripped = line.strip()
    return bool(re.match(r"^\|[\s\-:|]+\|$", stripped))


def chunk_markdown(
    text: str,
    filename: str,
    chunk_size: int = 1500,
    overlap: int = 200,
) -> list[dict]:
    lines = text.split("\n")
    chunks: list[dict] = []
    current_heading = ""

    # First pass: group lines into sections by heading, keeping tables intact
    sections: list[tuple[str, list[str]]] = []  # (heading, content_blocks)
    current_blocks: list[str] = []
    table_buffer: list[str] = []
    in_table = False

    for line in lines:
        if _is_table_line(line) or _is_table_separator(line):
            # Accumulate table lines
            if not in_table and current_blocks:
                # Flush any text before the table as a separate block
                pass
            in_table = True
            table_buffer.append(line)
        else:
            # Flush any accumulated table as a single block
            if in_table:
                current_blocks.append("\n".join(table_buffer))
                table_buffer = []
                in_table = False

            if line.startswith("#"):
                # Flush previous section
                if current_blocks:
                    sections.append((current_heading, current_blocks))
                    current_blocks = []
                current_heading = line.strip()
            else:
                if line.strip():
                    current_blocks.append(line)

    # Flush remaining table or text
    if table_buffer:
        current_blocks.append("\n".join(table_buffer))
    if current_blocks:
        sections.append((current_heading, current_blocks))

    # Second pass: chunk within each section, keeping tables intact
    for heading, blocks in sections:
        # Join non-table blocks into text, but keep tables as atomic units
        text_buffer: list[str] = []
        current_len = 0

        def flush_chunk(sentences: list[str]) -> None:
            chunk_text = " ".join(sentences).strip()
            if chunk_text:
                full_text = f"{heading}\n{chunk_text}" if heading else chunk_text
                chunks.append({
                    "text": full_text,
                    "filename": filename,
                    "heading": heading,
                })

        current_chunk_sentences: list[str] = []
        current_len = 0

        for block in blocks:
            is_table = _is_table_line(block.split("\n")[0]) if block else False

            if is_table:
                # Tables are atomic — flush current text chunk, then emit table
                if current_chunk_sentences:
                    flush_chunk(current_chunk_sentences)
                    current_chunk_sentences = []
                    current_len = 0

                # If the table itself exceeds chunk_size, still keep it whole
                table_text = block.strip()
                full_text = f"{heading}\n{table_text}" if heading else table_text
                chunks.append({
                    "text": full_text,
                    "filename": filename,
                    "heading": heading,
                })
            else:
                # Regular text — sentence-level chunking
                sentences = _split_sentences(block)
                for sentence in sentences:
                    sent_len = len(sentence) + 1

                    if current_len + sent_len > chunk_size and current_chunk_sentences:
                        flush_chunk(current_chunk_sentences)

                        # Build overlap from tail
                        overlap_sentences: list[str] = []
                        overlap_len = 0
                        for s in reversed(current_chunk_sentences):
                            if overlap_len + len(s) + 1 > overlap:
                                break
                            overlap_sentences.insert(0, s)
                            overlap_len += len(s) + 1

                        current_chunk_sentences = overlap_sentences
                        current_len = overlap_len

                    current_chunk_sentences.append(sentence)
                    current_len += sent_len

        # Flush remaining sentences in this section
        if current_chunk_sentences:
            flush_chunk(current_chunk_sentences)

    return chunks
