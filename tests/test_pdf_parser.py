# tests/test_pdf_parser.py

from pathlib import Path
from ragicane.pdf_parser import extract_raw_text


def test_extract_raw_text_nonempty(tmp_path):
    """
    Copy the sample ‘AL012018_Alberto.pdf’ to a temporary location and
    verify extract_raw_text() returns a non-empty string containing a known keyword.
    """
    root = Path(__file__).parent.parent
    sample = root / "sample_reports" / "AL012018_Alberto.pdf"
    print(f"Root: {root}")
    print(f"Sample location: {sample}")
    assert sample.exists(), f"Sample PDF not found at {sample}"

    # Copy into tmp_path
    dst = tmp_path / "test.pdf"
    dst.write_bytes(sample.read_bytes())

    # Call the function
    text = extract_raw_text(dst)

    assert isinstance(text, str)
    assert len(text) > 50
    # Check for a known phrase (“Alberto” or “Tropical”)
    assert ("Alberto" in text) or ("Tropical" in text)
