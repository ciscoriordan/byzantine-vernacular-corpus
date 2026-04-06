#!/usr/bin/env python3
"""
Fetch the Chronicle of Moreas (Χρονικόν του Μορέως) from kastra.eu.

The full text is available in monotonic Greek at kastra.eu, based on
the edition by Petros Kalonaros (Dimitrakos, 1940). The underlying
text is public domain (14th century anonymous work; 1940 edition
is also out of copyright).

The HTML is structured as a 4-column table:
  col 1: section markers (ignored)
  col 2: line numbers (ignored)
  col 3: verse text (extracted)
  col 4: annotations/glosses with class='pk' (ignored)

Headers have class='ho' and are also ignored.
"""

import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / "texts"
URL = "https://www.kastra.eu/infxrngr.php"


class ChronicleExtractor(HTMLParser):
    """Extract only the verse text (column 3) from the Chronicle table."""

    def __init__(self):
        super().__init__()
        self.verses = []
        self.in_table = False
        self.in_row = False
        self.col_index = 0
        self.current_text = []
        self.skip = False  # True when in class='ho' or class='pk' cells

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "table" and attrs_dict.get("id") == "xron":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.col_index = 0
        elif self.in_table and self.in_row and tag == "td":
            self.col_index += 1
            classes = attrs_dict.get("class", "")
            # Skip header cells and annotation cells
            if "ho" in classes or "pk" in classes:
                self.skip = True
            else:
                self.skip = False
            self.current_text = []
        elif tag == "b":
            pass  # Keep bold text content
        elif tag in ("script", "style"):
            self.skip = True

    def handle_endtag(self, tag):
        if self.in_table and self.in_row and tag == "td":
            if self.col_index == 3 and not self.skip:
                text = "".join(self.current_text).strip()
                if text and text != "\xa0":  # Skip &nbsp;
                    self.verses.append(text)
            self.current_text = []
            self.skip = False
        elif self.in_table and tag == "tr":
            self.in_row = False
            self.col_index = 0
        elif tag == "table" and self.in_table:
            self.in_table = False
        elif tag in ("script", "style"):
            self.skip = False

    def handle_data(self, data):
        if self.in_table and self.in_row and self.col_index == 3 and not self.skip:
            self.current_text.append(data)

    def handle_entityref(self, name):
        if self.in_table and self.in_row and self.col_index == 3 and not self.skip:
            self.current_text.append(f"&{name};")

    def handle_charref(self, name):
        if self.in_table and self.in_row and self.col_index == 3 and not self.skip:
            self.current_text.append(chr(int(name)))


def main():
    TEXTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading from kastra.eu...")
    req = urllib.request.Request(URL, headers={
        "User-Agent": "byzantine-vernacular-corpus/1.0 (research project)"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    print(f"Downloaded {len(html):,} bytes of HTML")

    parser = ChronicleExtractor()
    parser.feed(html)

    text = "\n".join(parser.verses)
    # Clean up any remaining whitespace issues
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    outpath = TEXTS_DIR / "chronikon_tou_moreos.txt"
    outpath.write_text(text, encoding="utf-8")

    lines = [l for l in text.split("\n") if l.strip()]
    words = len(text.split())
    print(f"Saved {outpath.name}: {words:,} words, {len(lines):,} lines, {len(text):,} chars")
    print(f"\nFirst 5 lines:")
    for l in lines[:5]:
        print(f"  {l}")
    print(f"\nLast 5 lines:")
    for l in lines[-5:]:
        print(f"  {l}")


if __name__ == "__main__":
    main()
