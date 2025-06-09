import asyncio
from pathlib import Path
from ragicane.pdf_parser import extract_raw_text
from ragicane.text_splitter import (
    simple_split,
    clean_chunks,
)  # or your LangChain splitter


async def process_pdf(path: Path):
    raw = await asyncio.to_thread(extract_raw_text, path)
    chunks = simple_split(raw)
    return clean_chunks(chunks)


async def ingest_directory(dir_path: Path):
    pdfs = list(dir_path.glob("*.pdf"))
    # use asyncio.to_thread so extract_raw_text and simple_split run off the event loop
    tasks = [process_pdf(p) for p in pdfs]
    chunks_map = await asyncio.gather(*tasks)
    return dict(zip(pdfs, chunks_map))


if __name__ == "__main__":
    import sys

    directory = Path(sys.argv[1])
    result = asyncio.run(ingest_directory(directory))
    for pdf, chunks in result.items():
        print(f"{pdf.name}: {len(chunks)} chunks")
