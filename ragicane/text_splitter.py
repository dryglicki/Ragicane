from typing import List
import re
import nltk
import spacy

nltk.download('punkt')

nlp = spacy.load("en_core_web_sm")

def simple_split(text: str, max_chars: int = 2000, overlap: int = 200) -> List[str]:
    """
    Splits `text` into chunks of up to `max_chars`, with `overlap` characters
    carried from the end of one chunk to the start of the next.
    Inputs:
      - text, str: input text string
      - max_chars, int: maximum length of string chunk
      - overlap, int: Number of characters to overlap

    Return:
      - List of chunks.
    """
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + max_chars, L)
        chunk = text[start:end]
        chunks.append(chunk)
        # Step forward by chunk_size - overlap
        start += max_chars - overlap
    return chunks

def sentence_chunk(text: str, max_words: int = 250) -> List[str]:
    """
    Splits text into chunks of up to `max_words` words, breaking only at sentence boundaries.
    """
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current = []
    count = 0
    for sent in sentences:
        words = sent.split()
        if count + len(words) > max_words and current:
            chunks.append(" ".join(current))
            current = []
            count = 0
        current.append(sent)
        count += len(words)
    if current:
        chunks.append(" ".join(current))
    return chunks

def clean_chunks(chunks: List[str]) -> List[str]:
    cleaned = []
    for chunk in chunks:
        doc = nlp(chunk)
        # Reassemble only full sentences
        sentences = [sent.text.strip() for sent in doc.sents]
        cleaned.append(" ".join(sentences))
    return cleaned

