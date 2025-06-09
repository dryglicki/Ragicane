# tests/test_text_splitter.py

import sys
import nltk

from ragicane.text_splitter import simple_split, sentence_chunk, clean_chunks


def test_simple_split_short_text():
    """
    If text length < max_chars, simple_split should return a single chunk identical to the input.
    """
    text = "Hello world!"
    chunks = simple_split(text, max_chars=50, overlap=10)
    assert chunks == ["Hello world!"]


def test_simple_split_multiple_chunks():
    """
    A string of length 120 with max_chars=50 & overlap=10 should produce >=2 chunks,
    each of length ≤ 50.
    """
    text = "A" * 120
    chunks = simple_split(text, max_chars=50, overlap=10)
    assert isinstance(chunks, list)
    assert len(chunks) >= 2
    assert all(isinstance(c, str) and len(c) <= 50 for c in chunks)


def test_sentence_chunk_splits_on_sentence_boundaries(monkeypatch):
    """
    sentence_chunk should split on full sentences, not break a sentence across chunks.
    With max_words=3, each sentence in the text below <=3 words, so
    we expect one chunk per sentence.
    """
    monkeypatch.setattr(
        nltk.tokenize,
        "sent_tokenize",
        lambda txt: ["One two three.", "Four five six.", "Seven eight."],
    )

    text = "One two three. Four five six. Seven eight."
    # Words per sentence: 3,3,2 → all <= max_words → 3 chunks
    chunks = sentence_chunk(text, max_words=3)
    assert chunks == ["One two three.", "Four five six.", "Seven eight."]


def test_clean_chunks_without_spacy(monkeypatch):
    """
    If spaCy or sentencizer isn't available (simulate by injecting an ImportError),
    clean_chunks should return the input chunks unchanged.
    """
    dummy_chunks = ["One sentence. Two sentences.", "Another chunk."]
    # Simulate spaCy import failure by placing a dummy in sys.modules
    monkeypatch.setitem(sys.modules, "spacy", None)

    result = clean_chunks(dummy_chunks)
    assert result == dummy_chunks


def test_clean_chunks_with_sentencizer():
    """
    If spaCy is installed (with sentencizer pipeline), clean_chunks should join sentences properly.
    We pass in two chunks; each chunk contains two sentences separated by ". ".
    clean_chunks should combine them into one chunk with exactly those sentences joined by a space.
    """
    # Create two chunks with clear sentence boundaries:
    chunk1 = "Sentence one. Sentence two."
    chunk2 = "Hello world! How are you?"

    # clean_chunks should produce:
    # ["Sentence one Sentence two", "Hello world How are you"]
    result = clean_chunks([chunk1, chunk2])
    assert isinstance(result, list)
    assert len(result) == 2

    # Each cleaned string should contain both sentences concatenated:
    assert "Sentence one" in result[0] and "Sentence two" in result[0]
    assert "Hello world" in result[1] and "How are you" in result[1]


def test_clean_chunks_preserves_full_sentences():
    chunk1 = "Hello world. Goodbye world."
    chunk2 = "Foo bar? Baz qux!"
    cleaned = clean_chunks([chunk1, chunk2])

    assert isinstance(cleaned, list) and len(cleaned) == 2
    assert "Hello world." in cleaned[0] and "Goodbye world." in cleaned[0]
    assert "Foo bar?" in cleaned[1] and "Baz qux!" in cleaned[1]
