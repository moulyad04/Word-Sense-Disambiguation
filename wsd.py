"""Deterministic, explainable Lesk-style word sense disambiguation."""
import re

STOP = set('a an the and or of to in on for with by from is are was were be been this that it its as at our their we they has have had will can into during after before more he she his her i you my me them then than also very not no'.split())

def tokens(text):
    return set(w for w in re.findall(r'[a-z]+', text.lower().replace('_',' ')) if len(w)>1 and w not in STOP)

def signature(sense, mode='extended'):
    weights = {}
    def add(text, weight):
        for word in tokens(text):
            weights[word] = max(weights.get(word,0), weight)
    add(sense['definition'], 1 if mode == 'classic' else 3)
    if mode == 'extended':
        add(' '.join(sense['lemmas']),3)
        add(' '.join(sense['examples']),2)
        for relation in sense['hypernyms'] + sense['hyponyms']:
            add(relation['definition']+' '+' '.join(relation['lemmas']),1)
    return weights

def analyze(sentence, word, inventory, mode='extended'):
    word=word.strip().lower()
    if mode not in ('extended','classic'):
        raise ValueError('Unknown algorithm.')
    if word not in inventory:
        raise ValueError('Choose a word in the supported inventory.')
    if len(sentence)>2000 or not sentence.strip():
        raise ValueError('Enter a sentence of 1 to 2000 characters.')
    if word not in re.findall(r'[a-z]+',sentence.lower()):
        raise ValueError('The exact target word must appear in the sentence.')
    context=tokens(sentence)-{word}
    ranked=[]
    for sense in inventory[word]:
        sig=signature(sense,mode)
        matched=sorted(context & sig.keys())
        ranked.append({'id':sense['id'],'score':sum(sig[t] for t in matched),'matches':matched})
    ranked.sort(key=lambda row:-row['score']) # stable WordNet order for display only
    best=ranked[0]['score']
    tied=sum(row['score']==best for row in ranked)
    status='no_evidence' if best==0 else ('tied' if tied>1 else 'resolved')
    return {'word':word,'sentence':sentence,'mode':mode,'status':status,'selected':ranked[0]['id'] if status=='resolved' else None,'score':best,'margin':best-ranked[1]['score'] if len(ranked)>1 else best,'context':sorted(context),'ranked':ranked}
