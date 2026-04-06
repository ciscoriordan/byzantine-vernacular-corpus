#!/usr/bin/env python3
"""
Build a combined corpus from individual Byzantine vernacular Greek texts.

Outputs:
  - texts/corpus.txt: all texts concatenated, separated by markers
  - texts/corpus_stats.json: word counts and frequency data

Usage:
  python scripts/build_corpus.py
  python scripts/build_corpus.py --freq    # also output top-N frequency list
"""

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / "texts"

# Files to include in the corpus (order matters for readability)
CORPUS_FILES = [
    "digenes_akritas_escorial.txt",
    "digenes_death.txt",
    "ptochoprodromika.txt",
    "chronikon_tou_moreos.txt",
    "poulologos.txt",
    "gadarou_lykou_aloupous.txt",
    "paidiophrastos.txt",
    "porikologos.txt",
    "peri_gerontos.txt",
    "apokopos.txt",
    "apokopos_bergadi.txt",
    "erotokritos.txt",
]


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for Greek text."""
    # Remove punctuation but keep Greek diacritics
    tokens = []
    for word in text.split():
        # Strip leading/trailing punctuation
        word = word.strip(".,;:·!?\"'«»()[]{}—-–…")
        if word:
            tokens.append(word)
    return tokens


def normalize_token(token: str) -> str:
    """Lowercase and normalize a token for frequency counting."""
    return token.lower()


def build_corpus(include_freq: bool = False):
    """Build the combined corpus file."""
    corpus_parts = []
    stats = {"files": [], "total_words": 0, "total_chars": 0, "total_lines": 0}

    # Load manifest if available
    manifest_path = TEXTS_DIR / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            for entry in json.load(f):
                manifest[entry.get("file", "")] = entry

    for filename in CORPUS_FILES:
        filepath = TEXTS_DIR / filename
        if not filepath.exists():
            print(f"  SKIP {filename} (not found)")
            continue

        text = filepath.read_text(encoding="utf-8")
        words = len(text.split())
        lines = len([l for l in text.split("\n") if l.strip()])
        chars = len(text)

        meta = manifest.get(filename, {})
        title = meta.get("title", filename)

        corpus_parts.append(f"### {title} ###\n\n{text}")

        file_stat = {
            "file": filename,
            "title": title,
            "words": words,
            "lines": lines,
            "chars": chars,
        }
        stats["files"].append(file_stat)
        stats["total_words"] += words
        stats["total_chars"] += chars
        stats["total_lines"] += lines

        print(f"  {filename}: {words:,} words")

    # Write combined corpus
    corpus_text = "\n\n\n".join(corpus_parts)
    corpus_path = TEXTS_DIR / "corpus.txt"
    corpus_path.write_text(corpus_text, encoding="utf-8")
    print(f"\nCorpus: {stats['total_words']:,} words -> {corpus_path}")

    # Frequency analysis
    if include_freq:
        print("\nBuilding frequency list...")
        all_tokens = tokenize(corpus_text)
        freq = Counter(normalize_token(t) for t in all_tokens)
        stats["vocabulary_size"] = len(freq)
        stats["token_count"] = len(all_tokens)

        # Top 500 frequencies
        top = freq.most_common(500)
        stats["top_500"] = [{"word": w, "count": c} for w, c in top]

        # Write full frequency list
        freq_path = TEXTS_DIR / "frequencies.tsv"
        with open(freq_path, "w", encoding="utf-8") as f:
            f.write("word\tcount\n")
            for word, count in freq.most_common():
                f.write(f"{word}\t{count}\n")
        print(f"Frequencies: {len(freq):,} unique words -> {freq_path}")

    # Write stats
    stats_path = TEXTS_DIR / "corpus_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Stats: {stats_path}")


def main():
    parser = argparse.ArgumentParser(description="Build Byzantine vernacular corpus")
    parser.add_argument("--freq", action="store_true", help="Generate frequency list")
    args = parser.parse_args()

    print("Building Byzantine vernacular Greek corpus...\n")
    build_corpus(include_freq=args.freq)
    print("\nDone.")


if __name__ == "__main__":
    main()
