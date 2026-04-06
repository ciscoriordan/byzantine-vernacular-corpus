#!/usr/bin/env python3
"""
Export word frequencies from the Byzantine Vernacular Corpus in JSON format
compatible with dilemma's rank_forms.py.

Output format:
  {
    "_total_tokens": N,
    "_n_forms": N,
    "_sources": ["Byzantine Vernacular Corpus"],
    "forms": {"word": [count], ...}
  }

Usage:
  python scripts/export_freq_json.py                    # print to stdout
  python scripts/export_freq_json.py -o path/to/out.json
  python scripts/export_freq_json.py --dilemma          # write to ../dilemma/data/byz_vern_freq.json
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

TEXTS_DIR = Path(__file__).resolve().parent.parent / "texts"

# Same file list as build_corpus.py
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
    """Split on whitespace, strip punctuation, return non-empty tokens."""
    tokens = []
    for word in text.split():
        word = word.strip(".,;:·!?\"'«»()[]{}—-–…")
        if word:
            tokens.append(word)
    return tokens


def build_freq() -> tuple[Counter, int]:
    """Read all corpus texts and return (frequency counter, total tokens)."""
    freq = Counter()
    total = 0
    for filename in CORPUS_FILES:
        path = TEXTS_DIR / filename
        if not path.exists():
            print(f"  SKIP {filename} (not found)", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        tokens = tokenize(text)
        lowered = [t.lower() for t in tokens]
        freq.update(lowered)
        total += len(lowered)
        print(f"  {filename}: {len(tokens):,} tokens", file=sys.stderr)
    return freq, total


def main():
    parser = argparse.ArgumentParser(
        description="Export Byzantine Vernacular Corpus frequencies as JSON"
    )
    parser.add_argument("-o", "--output", type=str, help="Output file path")
    parser.add_argument(
        "--dilemma",
        action="store_true",
        help="Write to ../dilemma/data/byz_vern_freq.json",
    )
    args = parser.parse_args()

    print("Building frequency data...", file=sys.stderr)
    freq, total = build_freq()

    # Build output in the format rank_forms.py expects
    # Sort by descending frequency for readability
    forms = {}
    for word, count in freq.most_common():
        forms[word] = [count]

    data = {
        "_total_tokens": total,
        "_n_forms": len(forms),
        "_sources": ["Byzantine Vernacular Corpus"],
        "forms": forms,
    }

    # Determine output path
    if args.dilemma:
        out_path = Path(__file__).resolve().parent.parent.parent / "dilemma" / "data" / "byz_vern_freq.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"\nWrote {len(forms):,} forms ({total:,} tokens) -> {out_path}", file=sys.stderr)
    elif args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"\nWrote {len(forms):,} forms ({total:,} tokens) -> {out_path}", file=sys.stderr)
    else:
        json.dump(data, sys.stdout, ensure_ascii=False)
        print(f"\n\n{len(forms):,} forms, {total:,} tokens", file=sys.stderr)


if __name__ == "__main__":
    main()
