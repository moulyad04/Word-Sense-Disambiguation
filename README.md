# Sense Atlas - Exercise 5

Advanced Natural Language Processing (AML23702), CO5 / L3.

A complete frontend for word sense disambiguation, a WordNet sense explorer, and a transparent evaluation view. All 90 noun senses for 12 target words come from Princeton WordNet 3.0, exported with NLTK. The website works with bundled data and needs no API key or server-side NLP service.

## Open the website

From this folder, run:

```powershell
python -m http.server 8785 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8785 in your browser. Use the HTTP address rather than double-clicking index.html, because browsers restrict loading JSON through file URLs. Python 3.11+ is sufficient to serve the finished website; no pip installation is required for viewing it.

## What you can do

- Enter a sentence and choose a supported noun: bank, bat, crane, plant, seal, mouse, spring, match, bark, bass, light or draft.
- Compare gloss-only and weighted extended Lesk-style methods. Both are original implementations using WordNet data, not wrappers around NLTK's built-in lesk.
- Inspect the selected definition, synonyms, evidence words, ranked senses and raw score. Zero evidence and tied winners produce an abstention.
- Explore all candidate senses, direct hypernyms/hyponyms, meronyms and recorded lemma-level antonyms.
- Review the 24 manually annotated examples, compare methods, filter results and open examples in the workspace.
- Export an individual analysis, the sense inventory, the sample annotations and the short analysis report.

No sentences are transmitted to an external service or saved in browser storage. Only local static files are requested. Scores are lexical overlap evidence, not probabilities or calibrated confidence.

## Required deliverables

| Lab requirement | Deliverable |
|---|---|
| Sense inventory / annotations | `outputs/sense_inventory.json`, `data/samples.csv` |
| WSD results for sample text | `outputs/wsd_results.csv` (48 rows: 24 samples x 2 methods) |
| Short analysis report | `outputs/analysis_report.md` and website Methodology view |
| Proper frontend | `dist/index.html`, `dist/styles.css`, `dist/app.js` |
| Evaluation and reproducibility | `outputs/evaluation.json`, tests and data export script |

## Rebuild the data (optional)

The served website already includes WordNet-derived data. To reproduce it from the corpus:

```powershell
python -m pip install -r requirements.txt
python -m nltk.downloader -d data/nltk_data wordnet
python tools/build_data.py
```

The exporter inserts the local corpus directory into NLTK's search path. The `data/nltk_data` download and temporary development `.deps` folder are excluded from version control. WordNet's license is included in `dist/WORDNET-LICENSE.txt` and must accompany redistributed definitions.

## Verify

```powershell
python -m unittest discover -s tests -v
node tests/verify_browser_algorithm.cjs
```

Python tests require no third-party libraries because the sense inventory is pre-exported. The Node check verifies all 48 browser predictions against the Python reference outputs.

## Scope and evaluation

Only the twelve listed English noun targets are supported, and the exact target spelling must appear in the sentence. Context uses lowercase alphabetic tokens, stopword removal and set overlap; there is no stemming, lemmatization or negation handling. The extended method weights gloss and synonyms at 3, examples at 2, and direct hypernym/hyponym text at 1. A token contributes its maximum field weight once.

The 24 educational sentences are manually labelled and authored with knowledge of the WordNet definitions, often sharing their vocabulary. They are not a held-out benchmark. Both methods achieve 21/24 correct (87.5%) and abstain on three examples in this run; resolved-only accuracy is 100%, which does not imply overall accuracy of 100%. The analysis report discusses the failures and limited generalizability.

## Formatted lab report

The PDF report is located at `reports/Exp05_Word_Sense_Disambiguation.pdf`. It follows the lab report structure with Department header (AIML AML23702), blue headings, Times body text, numbered pages, website screenshots, and filled evaluation sheet.

Install `requirements-report.txt` and run `python tools/build_report.py` to regenerate the report under `output/pdf/`.

Repository: https://github.com/moulyad04/Word-Sense-Disambiguation
