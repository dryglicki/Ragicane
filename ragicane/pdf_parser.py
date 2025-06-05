#!/usr/bin/env python3
from pathlib import Path
import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LAParams, LTTextBoxHorizontal

def extract_raw_text(pdf_path: Path) -> str:
    '''
    Extracts text from a PDF file.
    
    Inputs:
      - pdf_path: Pathlib object
    Returns:
      - string
    '''

    laparams = LAParams(
            line_margin = 0.5,
            char_margin = 2.0,
            word_margin = 0.1
            )

    pages: list[str] = []

    for page_layout in extract_pages(str(pdf_path), laparams=laparams):
        # collect grid points and text for each text box
        boxes: list[tuple[float, float, str]] = []
        for element in page_layout:
            if not isinstance(element, LTTextBoxHorizontal): continue
            text = element.get_text().strip()
            if not text: continue

            # Drop the page numbers.
            if re.fullmatch(r"\d+", text): continue

            # Drop common headers/footers
            if re.match(
                    r"^(Tropical Storm|TROPICAL CYCLONE REPORT|NATIONAL HURRICANE CENTER|\w+:|\s*Figure\s+\d+)",
                text,
                flags=re.IGNORECASE,
            ):
                continue

            # Now get bounding box
            x0, y0, x1, y1 = element.bbox
            boxes.append( (x0, y1, text.replace('\n', ' ')) )

        # sort by y1 descending (top-down), then by x0 ascending (left-right)
        boxes.sort(key = lambda tup: (-tup[1], tup[0]))
        page_txt = " ".join([t for _, _, t in boxes])
        pages.append(page_txt)

    full_text = '\n\n'.join(pages)

    # Collapse whitespace/newlines into a single space

    full_text = re.sub(r"\s+", " ", full_text)

    return full_text.strip()

