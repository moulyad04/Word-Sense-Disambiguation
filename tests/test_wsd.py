import json
import unittest
from pathlib import Path
from wsd import analyze, tokens

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'dist/assets/wordnet-data.json').read_text(encoding='utf-8'))
INV=DATA['inventory']

class WSDTests(unittest.TestCase):
    def test_context_tokenization(self):
        self.assertEqual(tokens('The MOUSE, mouse, and screen 123.'),{'mouse','screen'})

    def test_financial_and_river_contexts(self):
        self.assertEqual(analyze('The bank accepts deposits for lending.', 'bank',INV)['selected'],'depository_financial_institution.n.01')
        self.assertEqual(analyze('They walked along the bank beside the river water.', 'bank',INV)['selected'],'bank.n.01')

    def test_zero_evidence_abstains(self):
        result=analyze('The bank is here.', 'bank', INV)
        self.assertEqual(result['status'],'no_evidence')
        self.assertIsNone(result['selected'])

    def test_ties_abstain(self):
        result=analyze('She deposited money into her bank account.','bank',INV)
        self.assertEqual(result['status'],'tied')
        self.assertIsNone(result['selected'])

    def test_input_validation(self):
        for sentence,word,mode in [('Hello world','bank','extended'),('The bank','unknown','extended'),('The bank','bank','fake'),('bank'*1000,'bank','extended')]:
            with self.assertRaises(ValueError): analyze(sentence,word,INV,mode)

    def test_gold_senses_and_saved_predictions(self):
        for r in DATA['results']:
            self.assertIn(r['gold'],{s['id'] for s in INV[r['word']]})
            actual=analyze(r['sentence'],r['word'],INV,r['mode'])
            for key in ('selected','score','status','ranked'):
                self.assertEqual(actual[key],r[key])

    def test_metrics_include_abstentions(self):
        for mode in ('classic','extended'):
            rows=[r for r in DATA['results'] if r['mode']==mode]
            metric=DATA['evaluation'][mode]
            self.assertEqual(metric['correct'],sum(r['correct'] for r in rows))
            self.assertEqual(metric['accuracy'],metric['correct']/24)
            self.assertEqual(metric['coverage'],sum(r['selected'] is not None for r in rows)/24)

if __name__=='__main__': unittest.main()
