"""
Wordlist for wallet wallet phrases.

The words live in `wordlist.txt` next to this module rather than inline, because
there are several thousand of them. See that file for the source and licence.

A phrase is meant to be written on paper or read out loud, which a hex id never
was, so the list is filtered to words of at least five letters and the source is
one curated for exactly this purpose — a raw dictionary cannot be made safe by
rules alone.
"""

from pathlib import Path

WORDS_PER_PHRASE = 6


def _load_words():
    with Path(__file__).with_name("wordlist.txt").open(encoding="utf-8") as handle:
        return tuple(line.strip() for line in handle if line.strip() and not line.startswith("#"))


WORDS = _load_words()
