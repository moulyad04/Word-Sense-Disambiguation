# Exercise 5 - Word Sense Disambiguation with WordNet

## Aim and scope
Develop a knowledge-based WSD system, identify competing meanings, explore lexical relations, and apply a WSD algorithm to sample sentences. Sense Atlas provides a polished local website with a live sentence workspace, a sense explorer, evaluation tables and downloadable outputs. Scope is English noun senses for twelve explicit target words: bank, bat, crane, plant, seal, mouse, spring, match, bark, bass, light, draft. The exact target form must occur in the input. Other parts of speech and unrestricted vocabulary are outside scope.

## Corpus and annotation
Princeton WordNet 3.0 supplies 90 candidate noun synsets, exported through NLTK 3.10.3. Each record includes definitions, synonyms, examples, direct hypernyms/hyponyms, meronyms and lemma-level antonyms when available. The original WordNet copyright and license are included. The 24 sample sentences (two per target word) have manually assigned gold synset IDs. These are educational examples written with knowledge of the definitions and frequently share gloss vocabulary; they are not an independent or held-out benchmark. Labels are checked for membership in each target inventory.

## Pipeline and methodology
CSV sentence + target -> lowercase alphabetic tokens -> stopword removal -> distinct context words excluding the target -> WordNet candidate signatures -> overlap scoring -> unique positive winner or abstention -> annotated results and relations.

The gloss-only variant uses candidate definition words at weight 1. The extended variant adds definitions and synonyms (weight 3), usage examples (weight 2), and direct hypernym/hyponym definitions and lemmas (weight 1). A context token contributes only its maximum field weight once. These are custom Lesk-style variants, not calls to NLTK's built-in lesk. Meronyms and antonyms are displayed for lexical exploration but are not used in scoring. No tuning or training on sample labels occurs. There is no stemming, lemmatization, part-of-speech tagging, word-order modelling, negation handling or semantic embedding.

score(s, C) = sum(weight_s(t) for t in distinct_context intersect signature_s)

If the highest score is zero or shared by multiple senses, no sense is selected. WordNet order only determines the displayed order of tied candidates. Scores and winner margins are evidence measures, not probabilities or calibrated confidence.

## Actual evaluation
| Method | Correct / total | Accuracy | Coverage | Selective accuracy |
|---|---|---|---|---|
| classic | 21 / 24 | 87.5% | 87.5% | 100.0% |
| extended | 21 / 24 | 87.5% | 87.5% | 100.0% |

Accuracy counts abstentions as misses. Coverage is the fraction receiving a prediction. Selective accuracy measures correct predictions among resolved cases only. Both variants produce identical aggregate scores on this set, so no performance improvement from the extended signature is claimed. No confusion-matrix or classifier precision/recall is substituted for synset-match accuracy.

## Error and abstention analysis

### classic
- Sample 01 (bank): She deposited money into her bank account. Gold: `depository_financial_institution.n.01`. Status: tied; score 1; top candidates: depository_financial_institution.n.01, savings_bank.n.02. The model abstained rather than resolving an unsupported distinction.
- Sample 04 (bat): The player raised his bat to hit the ball. Gold: `bat.n.05`. Status: tied; score 1; top candidates: bat.n.02, bat.n.05. The model abstained rather than resolving an unsupported distinction.
- Sample 20 (bass): The fisherman caught a freshwater bass in the lake. Gold: `bass.n.08`. Status: tied; score 1; top candidates: freshwater_bass.n.01, bass.n.08. The model abstained rather than resolving an unsupported distinction.

### extended
- Sample 01 (bank): She deposited money into her bank account. Gold: `depository_financial_institution.n.01`. Status: tied; score 3; top candidates: depository_financial_institution.n.01, savings_bank.n.02. The model abstained rather than resolving an unsupported distinction.
- Sample 04 (bat): The player raised his bat to hit the ball. Gold: `bat.n.05`. Status: tied; score 3; top candidates: bat.n.02, bat.n.05. The model abstained rather than resolving an unsupported distinction.
- Sample 20 (bass): The fisherman caught a freshwater bass in the lake. Gold: `bass.n.08`. Status: tied; score 3; top candidates: freshwater_bass.n.01, bass.n.08. The model abstained rather than resolving an unsupported distinction.

Even familiar financial context can tie the financial-institution and savings-container senses when only the shared word “money” overlaps. Fine-grained WordNet senses can also share definition words. A larger signature does not solve contextual ambiguity automatically. Displayed lexical matches explain the scoring, but do not establish that the selected sense is linguistically correct.

## Strengths, limitations and extensions
The pipeline is deterministic, auditable and usable without APIs or credentials. Browser and Python reference implementations are verified against the same exported predictions. The interface separates selected senses from abstentions and exposes every candidate.

Exact lexical overlap is brittle under paraphrases and inflections, lacks discourse understanding, and ignores negation. Results on a small gloss-informed collection overestimate general-purpose performance. The fixed noun inventory cannot handle arbitrary target words, and noun interpretations may be wrong when the target is actually used as a verb. Signature length can favour broad senses. Better evaluation would use independently annotated contextual corpora, more diverse sentences, and agreement checks. Method extensions could add lemmatization, part-of-speech filtering and contextual embeddings while retaining transparent baselines.

## Verification and deliverables
Seven Python tests cover tokenization, distinct contexts, zero evidence, ties, invalid input, gold membership, saved predictions and metric denominators. The Node check verifies all 48 browser predictions against the Python reference implementation. Browser review covers analysis, examples, exploration, filters, exports, validation states and narrow-screen layout.

Required outputs: sense_inventory.json, wsd_results.csv and this analysis report. Supporting files: samples.csv, evaluation.json, frontend source and deterministic data-export script. The served downloads mirror the generated outputs. See README.md for setup and reproduction instructions.

## References
- NLTK WordNet interface: https://www.nltk.org/howto/wordnet.html
- NLTK WSD / Lesk documentation: https://www.nltk.org/api/nltk.wsd.html
- Princeton WordNet: https://wordnet.princeton.edu/
- WordNet license: dist/WORDNET-LICENSE.txt
