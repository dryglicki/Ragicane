# tests/test_ingest_pipeline.py

import pytest
from pathlib import Path

from ragicane.ingest_pipeline import ingest_directory


@pytest.mark.asyncio
async def test_ingest_directory_single_pdf(tmp_path):
    """
    Copy the sample PDF into tmp_path and run ingest_directory(tmp_path).
    Expect a dict with one key (the PDF Path) and a list of chunks (length ≥1).
    """
    root = Path(__file__).parent.parent
    sample = root / "sample_reports" / "AL012018_Alberto.pdf"
    assert sample.exists(), "Sample PDF missing from sample_reports/"

    # 1) Copy sample into tmp_path
    dest = tmp_path / "report.pdf"
    dest.write_bytes(sample.read_bytes())

    # 2) Call ingest_directory
    result = await ingest_directory(tmp_path)

    # 3) Check result
    assert isinstance(result, dict)
    assert dest in result

    chunks = result[dest]
    assert isinstance(chunks, list)
    assert len(chunks) >= 1

    # Each chunk should be a non-empty string
    assert all(isinstance(c, str) and len(c) > 0 for c in chunks)


@pytest.mark.asyncio
async def test_ingest_directory_empty_folder(tmp_path):
    """
    If the directory has no PDFs, ingest_directory should return an empty dict rather than error.
    """
    # tmp_path is empty by default
    result = await ingest_directory(tmp_path)
    assert result == {}
