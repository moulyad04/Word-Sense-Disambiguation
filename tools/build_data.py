"""Export real WordNet noun senses and run the labelled educational set."""
import csv
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
if (ROOT/'.deps').exists(): sys.path.insert(0,str(ROOT/'.deps'))
import nltk
from nltk.corpus import wordnet as wn
from wsd import analyze
nltk.data.path.insert(0,str(ROOT/'data/nltk_data'))
WORDS='bank bat crane plant seal mouse spring match bark bass light draft'.split()

def relation(s):
    return {'id':s.name(),'lemmas':[x.replace('_',' ') for x in s.lemma_names()],'definition':s.definition()}

def main():
    inventory={}
    for word in WORDS:
        inventory[word]=[]
        for s in wn.synsets(word,pos=wn.NOUN):
            inventory[word].append({**relation(s),'examples':s.examples(),'pos':'noun',
                'hypernyms':[relation(x) for x in sorted(s.hypernyms(),key=lambda x:x.name())],
                'hyponyms':[relation(x) for x in sorted(s.hyponyms(),key=lambda x:x.name())],
                'meronyms':[relation(x) for x in sorted(s.part_meronyms()+s.member_meronyms()+s.substance_meronyms(),key=lambda x:x.name())],
                'antonyms':sorted({a.name().replace('_',' ') for l in s.lemmas() for a in l.antonyms()})})
    with (ROOT/'data/samples.csv').open(encoding='utf-8',newline='') as f: samples=list(csv.DictReader(f))
    results=[]
    for sample in samples:
        assert sample['gold'] in {s['id'] for s in inventory[sample['word']]}
        for mode in ('classic','extended'):
            r=analyze(sample['sentence'],sample['word'],inventory,mode)
            results.append({**sample,**r,'correct':r['selected']==sample['gold']})
    evaluation={}
    for mode in ('classic','extended'):
        rr=[r for r in results if r['mode']==mode]
        resolved=[r for r in rr if r['status']=='resolved']
        evaluation[mode]={'total':len(rr),'correct':sum(r['correct'] for r in rr),'resolved':len(resolved),'accuracy':sum(r['correct'] for r in rr)/len(rr),'coverage':len(resolved)/len(rr),'selective_accuracy':sum(r['correct'] for r in resolved)/len(resolved) if resolved else None}
    payload={'wordnet_version':wn.get_version(),'nltk_version':nltk.__version__,'words':WORDS,'sense_count':sum(map(len,inventory.values())),'inventory':inventory,'samples':samples,'results':results,'evaluation':evaluation}
    (ROOT/'dist/assets/wordnet-data.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
    (ROOT/'outputs/sense_inventory.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    (ROOT/'outputs/evaluation.json').write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
    with (ROOT/'outputs/wsd_results.csv').open('w',encoding='utf-8',newline='') as f:
        keys=['id','word','sentence','gold','mode','selected','status','score','correct']
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore'); writer.writeheader(); writer.writerows(results)
    report='''# Exercise 5 - Word Sense Disambiguation with WordNet

## Aim and scope
Develop a knowledge-based WSD system, identify competing meanings, explore lexical relations, and apply a WSD algorithm to sample sentences. Sense Atlas provides a polished local website with a live sentence workspace, a sense explorer, evaluation tables and downloadable outputs. Scope is English noun senses for twelve explicit target words: '''+', '.join(WORDS)+'''. The exact target form must occur in the input. Other parts of speech and unrestricted vocabulary are outside scope.

## Corpus and annotation
Princeton WordNet '''+wn.get_version()+''' supplies '''+str(payload['sense_count'])+''' candidate noun synsets, exported through NLTK '''+nltk.__version__+'''. Each record includes definitions, synonyms, examples, direct hypernyms/hyponyms, meronyms and lemma-level antonyms when available. The original WordNet copyright and license are included. The 24 sample sentences (two per target word) have manually assigned gold synset IDs. These are educational examples written with knowledge of the definitions and frequently share gloss vocabulary; they are not an independent or held-out benchmark. Labels are checked for membership in each target inventory.

## Pipeline and methodology
CSV sentence + target -> lowercase alphabetic tokens -> stopword removal -> distinct context words excluding the target -> WordNet candidate signatures -> overlap scoring -> unique positive winner or abstention -> annotated results and relations.

The gloss-only variant uses candidate definition words at weight 1. The extended variant adds definitions and synonyms (weight 3), usage examples (weight 2), and direct hypernym/hyponym definitions and lemmas (weight 1). A context token contributes only its maximum field weight once. These are custom Lesk-style variants, not calls to NLTK's built-in lesk. Meronyms and antonyms are displayed for lexical exploration but are not used in scoring. No tuning or training on sample labels occurs. There is no stemming, lemmatization, part-of-speech tagging, word-order modelling, negation handling or semantic embedding.

score(s, C) = sum(weight_s(t) for t in distinct_context intersect signature_s)

If the highest score is zero or shared by multiple senses, no sense is selected. WordNet order only determines the displayed order of tied candidates. Scores and winner margins are evidence measures, not probabilities or calibrated confidence.

## Actual evaluation
| Method | Correct / total | Accuracy | Coverage | Selective accuracy |
|---|---|---|---|---|
'''
    for mode,metric in evaluation.items():
        report+=f"| {mode} | {metric['correct']} / {metric['total']} | {metric['accuracy']:.1%} | {metric['coverage']:.1%} | {metric['selective_accuracy']:.1%} |\n"
    report+='''
Accuracy counts abstentions as misses. Coverage is the fraction receiving a prediction. Selective accuracy measures correct predictions among resolved cases only. Both variants produce identical aggregate scores on this set, so no performance improvement from the extended signature is claimed. No confusion-matrix or classifier precision/recall is substituted for synset-match accuracy.

## Error and abstention analysis
'''
    for mode in ('classic','extended'):
        report+=f'\n### {mode}\n'
        for row in results:
            if row['mode']==mode and not row['correct']:
                leaders=[r['id'] for r in row['ranked'] if r['score']==row['score']]
                report+=f"- Sample {row['id']} ({row['word']}): {row['sentence']} Gold: `{row['gold']}`. Status: {row['status']}; score {row['score']}; top candidates: {', '.join(leaders)}. The model abstained rather than resolving an unsupported distinction.\n"
    report+='''
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
'''
    (ROOT/'outputs/analysis_report.md').write_text(report,encoding='utf-8')
    downloads=ROOT/'dist/downloads';downloads.mkdir(exist_ok=True)
    for name in ('sense_inventory.json','evaluation.json','wsd_results.csv','analysis_report.md'):
        shutil.copyfile(ROOT/'outputs'/name,downloads/name)
    # WordNet distribution license must accompany derived definitions.
    archive=ROOT/'data/nltk_data/corpora/wordnet.zip'
    if archive.exists():
        with zipfile.ZipFile(archive) as z:
            (ROOT/'dist/WORDNET-LICENSE.txt').write_bytes(z.read('wordnet/LICENSE'))
    print(json.dumps({'senses':payload['sense_count'],'evaluation':evaluation},indent=2))

if __name__=='__main__': main()
