#!/usr/bin/env python3
"""
Fetch vernacular Byzantine Greek texts from Greek Wikisource (el.wikisource.org).

Uses both wikitext and rendered HTML APIs depending on the page type.
Pages that use <pages> transclusion (from scanned DjVu files) require
the rendered HTML approach; others work fine with wikitext stripping.

All texts on el.wikisource.org are public domain (the underlying works)
and the Wikisource contributions are CC BY-SA 3.0.
"""

import json
import re
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / "texts"
API_URL = "https://el.wikisource.org/w/api.php"
USER_AGENT = "byzantine-vernacular-corpus/1.0 (research project)"

# Each entry: (output_filename, list_of_page_titles, metadata_dict)
# method: "wikitext" for pages with inline text, "html" for <pages> transclusion
SOURCES = [
    (
        "digenes_akritas_escorial.txt",
        ["Διγενής_Ακρίτας_(χειρόγραφο_Εσκοριάλ)"],
        {
            "title": "Digenes Akritas (Escorial manuscript, excerpt)",
            "title_el": "Διγενής Ακρίτας (χειρόγραφο Εσκοριάλ)",
            "date": "12th century (MS 15th century)",
            "register": "vernacular epic",
            "method": "wikitext",
        },
    ),
    (
        "ptochoprodromika.txt",
        ["Πτωχοπροδρομικά"],
        {
            "title": "Ptochoprodromika",
            "title_el": "Πτωχοπροδρομικά",
            "date": "12th century",
            "register": "vernacular satire",
            "method": "wikitext",
        },
    ),
    (
        "erotokritos.txt",
        ["Ερωτόκριτος/Α", "Ερωτόκριτος/Β", "Ερωτόκριτος/Γ",
         "Ερωτόκριτος/Δ", "Ερωτόκριτος/Ε"],
        {
            "title": "Erotokritos",
            "title_el": "Ερωτόκριτος",
            "author": "Vitsentzos Kornaros",
            "date": "c. 1600-1610",
            "register": "Cretan Renaissance vernacular romance",
            "note": "Post-Byzantine but key vernacular Greek text",
            "method": "wikitext",
        },
    ),
    (
        "apokopos.txt",
        ["Απόκοπος"],
        {
            "title": "Apokopos",
            "title_el": "Απόκοπος",
            "author": "Bergadis",
            "date": "15th century",
            "register": "Cretan vernacular narrative poem",
            "method": "wikitext",
        },
    ),
    (
        "poulologos.txt",
        ["Πουλολόγος"],
        {
            "title": "Poulologos (Bird Parliament)",
            "title_el": "Πουλολόγος",
            "date": "14th century",
            "register": "vernacular beast satire",
            "method": "html",
        },
    ),
    (
        "gadarou_lykou_aloupous.txt",
        ["Γαδάρου,_λύκου_κι_αλουπούς_διήγησις_ωραία"],
        {
            "title": "Tale of the Donkey, Wolf, and Fox",
            "title_el": "Γαδάρου, λύκου κι αλουπούς διήγησις ωραία",
            "date": "15th century",
            "register": "vernacular beast fable",
            "method": "html",
        },
    ),
    (
        "paidiophrastos.txt",
        ["Διήγησις_παιδιόφραστος_των_τετραπόδων_ζώων"],
        {
            "title": "Paidiophrastos Diegesis (Tale of the Quadrupeds)",
            "title_el": "Διήγησις παιδιόφραστος των τετραπόδων ζώων",
            "date": "14th-15th century",
            "register": "vernacular beast fable",
            "method": "html",
        },
    ),
    (
        "porikologos.txt",
        ["Διήγησις_του_Πωρικoλόγου", "Ο_Πωρικολόγος_Πετρουπόλεως"],
        {
            "title": "Porikologos (Fruit Parliament, two versions)",
            "title_el": "Πωρικολόγος",
            "date": "14th-15th century",
            "register": "vernacular satire",
            "method": "html",
        },
    ),
    (
        "peri_gerontos.txt",
        ["Περί_γέροντος_να_μην_πάρη_κορίτσι"],
        {
            "title": "Peri Gerontos (About the Old Man Marrying a Girl)",
            "title_el": "Περί γέροντος να μην πάρη κορίτσι",
            "date": "14th-15th century",
            "register": "vernacular satire",
            "method": "html",
        },
    ),
    (
        "apokopos_bergadi.txt",
        ["Απόκοπος_του_Μπεργαδή"],
        {
            "title": "Apokopos (Bergadis edition from Wagner)",
            "title_el": "Απόκοπος του Μπεργαδή",
            "author": "Bergadis",
            "date": "15th century",
            "register": "Cretan vernacular narrative poem",
            "note": "Wagner 1874 edition",
            "method": "html",
        },
    ),
    (
        "digenes_death.txt",
        ["Ο_θάνατος_του_Διγενή", "Ο_Διγενής_ψυχομαχεί"],
        {
            "title": "Death of Digenes (folk ballads)",
            "title_el": "Ο θάνατος του Διγενή / Ο Διγενής ψυχομαχεί",
            "date": "medieval (folk tradition)",
            "register": "vernacular folk poetry",
            "method": "html",
        },
    ),
]


class HTMLTextExtractor(HTMLParser):
    """Extract plain text from rendered Wikisource HTML."""

    SKIP_TAGS = {"script", "style", "sup"}
    SKIP_CLASSES = {
        "mw-editsection", "reference", "reflist", "noprint",
        "navbox", "catlinks", "toc", "mw-headline",
    }

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "")
        if tag in self.SKIP_TAGS or any(c in classes for c in self.SKIP_CLASSES):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag in ("p", "br", "div"):
            self.text.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.text.append(data)


def fetch_wikitext(page_title: str) -> str:
    """Fetch raw wikitext for a page."""
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(f"API error for {page_title!r}: {data['error']}")
    return data["parse"]["wikitext"]["*"]


def fetch_rendered_html(page_title: str) -> str:
    """Fetch rendered HTML for a page (needed for <pages> transclusion)."""
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "text",
        "format": "json",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(f"API error for {page_title!r}: {data['error']}")
    return data["parse"]["text"]["*"]


def strip_wikitext(wikitext: str) -> str:
    """Remove wiki markup, keeping only the Greek text."""
    text = wikitext
    text = re.sub(r'\{\{[^}]*\}\}', '', text)
    text = re.sub(r'\[\[Κατηγορία:[^\]]*\]\]', '', text)
    text = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'\[\[([^\]]*)\]\]', r'\1', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    text = re.sub(r'<br\s*/?\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r"'{2,}", '', text)
    text = re.sub(r'^=+\s*.*?\s*=+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def html_to_text(html: str) -> str:
    """Convert rendered HTML to clean plain text."""
    parser = HTMLTextExtractor()
    parser.feed(html)
    text = "".join(parser.text)
    # Remove page number markers like [179]
    text = re.sub(r"\[\d+\]", "", text)
    # Remove navigation arrows
    text = re.sub(r"[←→]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    TEXTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []

    for filename, pages, metadata in SOURCES:
        outpath = TEXTS_DIR / filename
        method = metadata.pop("method", "wikitext")
        print(f"Fetching {metadata['title']}...")

        parts = []
        for page in pages:
            print(f"  - {page} ({method})")
            if method == "html":
                html = fetch_rendered_html(page)
                text = html_to_text(html)
            else:
                wikitext = fetch_wikitext(page)
                text = strip_wikitext(wikitext)
            parts.append(text)
            time.sleep(1)

        full_text = "\n\n".join(parts)
        outpath.write_text(full_text, encoding="utf-8")

        word_count = len(full_text.split())
        char_count = len(full_text)
        line_count = len([l for l in full_text.split("\n") if l.strip()])

        source_urls = [
            f"https://el.wikisource.org/wiki/{p.replace(' ', '_')}"
            for p in pages
        ]
        metadata["file"] = filename
        metadata["source"] = "el.wikisource.org"
        metadata["source_urls"] = source_urls
        metadata["license"] = "Public domain / CC BY-SA 3.0 (Wikisource)"
        metadata["words"] = word_count
        metadata["chars"] = char_count
        metadata["lines"] = line_count
        manifest.append(metadata)

        print(f"  -> {filename}: {word_count:,} words, {line_count:,} lines")

    manifest_path = TEXTS_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\nManifest written to {manifest_path}")

    total_words = sum(m["words"] for m in manifest)
    print(f"\nTotal corpus: {total_words:,} words across {len(manifest)} texts")


if __name__ == "__main__":
    main()
