# Byzantine Vernacular Greek Corpus

A collection of open-access vernacular (demotic) Byzantine and Cretan Renaissance Greek texts, compiled for use in frequency analysis and NLP tasks. Built to provide Byzantine vernacular training data for the [dilemma](https://github.com/ciscoriordan/dilemma) Greek lemmatizer.

## Corpus contents

The corpus currently contains ~186,000 words across 11 texts spanning the 12th-17th centuries.

| Text | Greek title | Date | Words | Register |
|------|------------|------|-------|----------|
| Digenes Akritas (Escorial MS, excerpt) | Διγενής Ακρίτας | 12th c. | 803 | vernacular epic |
| Ptochoprodromika | Πτωχοπροδρομικά | 12th c. | 371 | vernacular satire |
| Chronicle of Moreas | Χρονικόν του Μορέως | 14th c. | 73,348 | vernacular chronicle |
| Poulologos | Πουλολόγος | 14th c. | 5,117 | beast satire |
| Paidiophrastos Diegesis | Διήγησις παιδιόφραστος | 14th-15th c. | 8,197 | beast fable |
| Porikologos | Πωρικολόγος | 14th-15th c. | 1,447 | vernacular satire |
| Peri Gerontos | Περί γέροντος | 14th-15th c. | 1,680 | vernacular satire |
| Tale of the Donkey, Wolf, and Fox | Γαδάρου, λύκου κι αλουπούς | 15th c. | 4,422 | beast fable |
| Apokopos | Απόκοπος | 15th c. | 4,141 | Cretan narrative poem |
| Death of Digenes (folk ballads) | Ο θάνατος του Διγενή | medieval | 394 | folk poetry |
| Erotokritos | Ερωτόκριτος | c. 1600 | 85,872 | Cretan Renaissance romance |

Total: **~186,000 words**, vocabulary of **~26,000 unique forms**.

## Sources and licensing

All texts are public domain (medieval/early modern works whose copyright has long expired).

- **Wikisource texts** (el.wikisource.org): Wikisource contributions are CC BY-SA 3.0. Source editions include Wagner's *Carmina Graeca Medii Aevi* (Teubner, 1874) and various public domain editions.
- **Chronicle of Moreas**: From kastra.eu, based on the edition by Petros Kalonaros (Dimitrakos, 1940).

Full source URLs and metadata are in `texts/manifest.json`.

## Usage

### Fetch texts from sources

```bash
# Fetch Wikisource texts
python scripts/fetch_wikisource.py

# Fetch Chronicle of Moreas from kastra.eu
python scripts/fetch_chronicle_moreas.py
```

### Build combined corpus

```bash
# Build corpus.txt (all texts concatenated)
python scripts/build_corpus.py

# Build corpus with frequency analysis
python scripts/build_corpus.py --freq
```

This produces:
- `texts/corpus.txt` - combined corpus with text markers
- `texts/corpus_stats.json` - word counts per text
- `texts/frequencies.tsv` - word frequency list (with `--freq`)

## Directory structure

```
texts/           Raw text files and corpus outputs
  manifest.json  Metadata for all texts (source URLs, word counts, dates)
  corpus.txt     Combined corpus
  *.txt          Individual text files
scripts/         Fetch and build scripts
  fetch_wikisource.py       Download texts from el.wikisource.org
  fetch_chronicle_moreas.py Download Chronicle of Moreas from kastra.eu
  build_corpus.py           Combine texts into corpus with frequency analysis
```

## Texts not yet included

The following vernacular Byzantine texts are known but not yet available in open digital form, or require more work to obtain:

- **Digenes Akritas (Grottaferrata version)** - the most complete manuscript version; no open digital edition found
- **Livistros and Rodamne** (Λίβιστρος και Ροδάμνη) - 13th c. romance, ~4,700 verses; critical edition by Lendari (MIET, 2007) is in print, not online
- **Kallimachos and Chrysorroi** (Καλλίμαχος και Χρυσορρόη) - 14th c. romance; only available in print editions
- **Belthandros and Chrysantza** (Βέλθανδρος και Χρυσάντζα) - 14th c. romance; only in print
- **Byzantine Achilleid** (Αχιλληΐδα) - 13th-14th c. romance; Smith edition (Vienna, 1999) not freely available
- **War of Troy** (Πόλεμος της Τρωάδος) - Byzantine retelling; not found online
- **Chronicle of the Tocco** (Χρονικόν των Τόκκων) - 15th c. Epirote chronicle; Schiro edition (1975) not online
- **Imperios and Margarona** (Ιμπέριος και Μαργαρώνα) - 15th c. chivalric romance; MIET critical edition exists
- **Florios and Platziaflora** (Φλώριος και Πλατζιαφλώρα) - Byzantine romance adaptation
- **Sacrifice of Abraham** (Η Θυσία του Αβραάμ) - Cretan religious drama, ~1,144 verses
- **Erofili** (Ερωφίλη) - Cretan tragedy by Chortatsis
- **Spaneas** - 12th c. didactic poem

The Cambridge Grammar of Medieval and Early Modern Greek project assembled a ~3 million word electronic corpus of vernacular Greek texts (11th-18th c.), but this corpus does not appear to be publicly available.

The Thesaurus Linguae Graecae (TLG) contains many of these texts but requires institutional subscription.

## Notes on orthography

The texts in this corpus use a mix of orthographic conventions:

- **Polytonic** (e.g., Apokopos, beast fables from Wagner editions): ἐμᾶς, τὸν, ποὺ
- **Monotonic** (e.g., Chronicle of Moreas from Kalonaros): εμάς, τον, που
- **Mixed** (e.g., Erotokritos): some pages use polytonic, others monotonic

For NLP purposes, normalizing to monotonic before processing is recommended. The dilemma lemmatizer handles both conventions.
