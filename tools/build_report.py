"""Build the formatted Exercise 5 lab report from verified project outputs."""
import json
import platform
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, Image
from reportlab.pdfgen.canvas import Canvas

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'output/pdf/Exp05_Word_Sense_Disambiguation.pdf'
DATA=json.loads((ROOT/'dist/assets/wordnet-data.json').read_text(encoding='utf-8'))
BLUE=colors.HexColor('#245882')
BODY=ParagraphStyle('Body',fontName='Times-Roman',fontSize=11,leading=14,spaceAfter=9)
HEAD=ParagraphStyle('Heading',fontName='Times-Bold',fontSize=15,leading=19,textColor=BLUE,spaceBefore=10,spaceAfter=10,borderWidth=.6,borderColor=BLUE,borderPadding=4)
TITLE=ParagraphStyle('Title',fontName='Times-Bold',fontSize=17,leading=22,textColor=BLUE,alignment=TA_CENTER,spaceAfter=16)
CELL=ParagraphStyle('Cell',fontName='Times-Roman',fontSize=10,leading=12)
CODE=ParagraphStyle('Code',fontName='Courier',fontSize=8.5,leading=11,backColor=colors.HexColor('#f2f2f2'),borderPadding=9,spaceAfter=13)
story=[]
def p(text):story.append(Paragraph(text,BODY))
def h(text):story.append(Paragraph(text,HEAD))
def bullet(text):p('&#8226; '+text)
def page():story.append(PageBreak())
def table(headers,rows,widths):
    cells=[[Paragraph('<b>'+escape(str(v))+'</b>',CELL) for v in headers]]+[[Paragraph(escape(str(v)),CELL) for v in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.HexColor('#bfc4c8')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf2f7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.extend([t,Spacer(1,7)])
def screenshot(name):
    file=ROOT/'screenshots'/name
    w,h=ImageReader(str(file)).getSize()
    story.append(Image(str(file),width=480,height=480*h/w))
    story.append(Spacer(1,8))

story.append(Paragraph('LAB EXERCISE: 5',TITLE))
h('Aim / Objective')
p('Develop a word sense disambiguation (WSD) system using WordNet and lexical relations. Sense Atlas identifies competing meanings of ambiguous English nouns, applies Lesk-style overlap algorithms to sentence context, and presents the selected sense with inspectable lexical evidence through a complete responsive website.')
h('Expected Outcomes Addressed')
bullet('<b>Identify different senses of ambiguous words:</b> export all 90 noun synsets for 12 supported target words and display their definitions, synonyms and usage examples.')
bullet('<b>Use WordNet to explore lexical relations:</b> inspect direct hypernyms, hyponyms, meronyms and recorded lemma-level antonyms in the Sense explorer.')
bullet('<b>Apply a WSD algorithm to sample sentences:</b> compare gloss-only and extended Lesk-style variants on 24 manually annotated examples, with explicit abstention for ties or absent evidence.')
h('Tools &amp; Technologies Used')
table(['Category','Tool / version','Purpose'],[['Language / runtime',f'Python {platform.python_version()}','WordNet export, reference scoring, evaluation and tests'],['Lexical resource','Princeton WordNet '+DATA['wordnet_version'],'Noun synsets, definitions and lexical relations'],['NLP library','NLTK '+DATA['nltk_version'],'Access and export the original WordNet corpus'],['Frontend','HTML5, CSS3, JavaScript','Responsive workspace, sense exploration and exports'],['Report generation','ReportLab 4.x','Formatted PDF, tables and embedded screenshots'],['Verification','unittest and Node.js','Seven Python tests; cross-language prediction checks']],[105,140,235])
p('The finished website uses bundled WordNet-derived data and requires no API key. NLTK is required to rebuild the inventory, but not to view or operate the frontend.')
page()

h('Dataset / Corpus Description')
p('WordNet 3.0, accessed through NLTK, supplies 90 noun senses for bank, bat, crane, plant, seal, mouse, spring, match, bark, bass, light and draft. All noun senses for these targets are exported; verbs, adjectives, adverbs and unrestricted target vocabulary are outside the scope.')
p('The original educational sentence collection contains 24 records, two per target word. Each record includes an ID, exact target word, sentence and manually assigned gold WordNet synset ID. Sentences were authored with knowledge of the definitions and often share their vocabulary. This makes the collection suitable for explanation, but it is not an independent benchmark.')
table(['Property','Value'],[['Target vocabulary','12 ambiguous English nouns'],['Sense inventory','90 WordNet noun synsets'],['Annotated examples','24'],['Evaluation rows','48: 24 sentences x 2 algorithms'],['Data provenance','WordNet 3.0 plus original manually labelled sentences'],['Licensing','WordNet copyright and license included in dist/WORDNET-LICENSE.txt']],[160,320])
p('<b>Sample record:</b> "Move the mouse to control the cursor on the computer screen." Target: mouse. Gold sense: mouse.n.04 (computer pointing device). Gold labels are validated against each target inventory and are not used in scoring.')
h('System Architecture / Pipeline Design')
table(['Module','Operation','Output'],[['1. Resource export','Read WordNet noun synsets and direct relations','Bundled JSON inventory'],['2. Context processing','Lowercase; alphabetic tokens; fixed stopwords; remove target; deduplicate','Distinct content words'],['3. Signature construction','Build gloss-only or weighted lexical signatures','Candidate token weights'],['4. Disambiguation','Sum overlapping token weights; require unique positive winner','Sense or abstention'],['5. Interpretation','Expose definition, evidence and competing senses','Live frontend results'],['6. Evaluation','Compare predictions with manual gold IDs','CSV and metrics JSON']],[110,230,140])
page()

h('Backend Implementation')
p('<b>6.1 Approach / Algorithm</b>')
p('This is a knowledge-based system with no training phase. Python exports WordNet data, computes reference predictions, and evaluates the annotated collection. The browser runs an equivalent JavaScript implementation against the exported inventory, so live analysis does not require a remote inference service.')
p('<b>Gloss-only Lesk-style variant:</b> each distinct context word overlapping the candidate definition contributes one point. <b>Extended variant:</b> definition and synonym tokens have weight 3, example tokens weight 2, and direct hypernym/hyponym definition and lemma tokens weight 1. A token appearing in several fields contributes its maximum field weight once. Meronyms and antonyms support exploration but are excluded from scoring.')
story.append(Preformatted('score(s, C) = sum(weight_s(t)\n                  for t in C intersect signature_s)\n\nSelect s only when score(s,C) > 0\nand s is the unique highest-scoring candidate.',CODE))
p('A zero-overlap or tied result produces no selected sense. WordNet order only orders tied candidates for display. Scores and winner margins are lexical evidence, not probabilities or calibrated confidence. Both variants are original Lesk-style implementations; they do not call NLTK\'s built-in lesk function.')
p('<b>6.2 Key Code Snippets</b>')
story.append(Preformatted("# Real WordNet inventory\nfor synset in wn.synsets(word, pos=wn.NOUN):\n    definition = synset.definition()\n    examples = synset.examples()\n    synonyms = synset.lemma_names()\n    parents = synset.hypernyms()\n    children = synset.hyponyms()",CODE))
story.append(Preformatted("# Context overlap and abstention (simplified)\ncontext = tokens(sentence) - {word}\nscore = sum(signature[t] for t in context\n            if t in signature)\nstatus = 'no_evidence' if best == 0 else (\n    'tied' if tied > 1 else 'resolved')\nselected = ranked[0]['id'] if status == 'resolved' else None",CODE))
p('The complete reference algorithm is in wsd.py; the WordNet exporter is tools/build_data.py. dist/app.js contains the verified browser implementation.')
page()

h('Frontend / UI Implementation')
p('<b>7.1 Framework Choice:</b> HTML5, CSS3 and vanilla JavaScript form a complete local website. A simple HTTP server serves the static assets; sentence scoring runs in the browser.')
p('<b>7.2 Interface Features:</b> sentence input, target and method selection, example contexts, selected meaning, evidence tokens, ranked candidate scores, JSON export and responsive navigation.')
screenshot('workspace.png')
p('<b>Figure 1.</b> Working Sense Atlas frontend: a financial bank context receives a unique positive match. The evidence panel highlights deposits and lending. Original website screenshot, with aspect ratio preserved.')
page()

h('Frontend / UI Implementation (continued)')
screenshot('sense-explorer.png')
p('<b>Figure 2.</b> Sense explorer showing the computer-mouse sense, its electronic-device hypernym and mouse-button meronym. Search filters the actual WordNet inventory; missing relations are explicitly identified.')
bullet('<b>Sense explorer:</b> inspect all candidate noun meanings, definitions, synonyms, examples and direct lexical relations.')
bullet('<b>Evaluation:</b> switch methods, filter correct predictions and abstentions, inspect examples, and export all 48 annotated results.')
bullet('<b>Methodology:</b> review the pipeline, scope, scoring rules, limitations, references and downloadable deliverables. A narrow-screen layout was checked and captured in screenshots/mobile.png.')
page()

h('Sample Input &amp; Output')
examples=[DATA['results'][i] for i in range(len(DATA['results'])) if DATA['results'][i]['mode']=='extended' and DATA['results'][i]['id'] in ('02','03','12','14')]
table(['Target / sentence','Selected sense','Status / score'],[[r['word']+': '+r['sentence'],r['selected'],r['status']+' / '+str(r['score'])] for r in examples],[250,155,75])
p('<b>Ambiguous example:</b> "She deposited money into her bank account." The financial-institution and savings-container senses both score 3 under the extended method, so the system abstains. Adding a specific clue such as deposits and lending distinguishes the institutional sense.')
h('Results (Deliverable-Specific Outputs)')
table(['Required output','Delivered file / evidence'],[['Sense inventory or annotation output','outputs/sense_inventory.json; data/samples.csv'],['WSD results for sample text','outputs/wsd_results.csv: 48 rows across two methods'],['Short analysis report','outputs/analysis_report.md'],['Supporting evaluation','outputs/evaluation.json'],['Working frontend','dist/index.html; dist/styles.css; dist/app.js'],['Website screenshots','screenshots/workspace.png; sense-explorer.png; evaluation.png; mobile.png']],[170,310])
p('The website also offers downloads mirroring the generated inventory, results, metrics and analysis. Each prediction records its target, sentence, method, selected synset, status, score and correctness against the manual label.')
page()

h('Evaluation / Analysis')
table(['Method','Correct / total','Accuracy','Coverage','Selective accuracy'],[[mode,str(m['correct'])+' / '+str(m['total']),f"{m['accuracy']:.1%}",f"{m['coverage']:.1%}",f"{m['selective_accuracy']:.1%}"] for mode,m in DATA['evaluation'].items()],[100,90,85,85,120])
p('Accuracy uses all 24 examples and counts abstentions as misses. Coverage is the proportion receiving a prediction. Selective accuracy is measured only among resolved cases. Therefore 100% selective accuracy does not mean 100% overall accuracy. Both methods achieve the same aggregate results; no improvement from the extended signature is claimed.')
p('Both variants abstain on three cases: financial bank versus savings container, baseball turn versus hitting implement, and freshwater-bass flesh versus the generic fish sense. Exact word overlap cannot reliably resolve these fine-grained distinctions. The gloss-informed sample design limits generalizability, so these scores must not be presented as unseen-text benchmark performance.')
p('<b>Verification:</b> all seven Python tests passed. The Node check matched all 48 browser predictions to the Python reference, including statuses, scores, margins and evidence words. Browser checks covered input validation, abstentions, exploration, evaluation filters, JSON export, download availability and mobile layout. No console errors were observed during the review.')
h('Challenges Faced &amp; Solutions')
bullet('<b>Competing meanings share vocabulary:</b> display all scores and abstain on ties rather than silently choosing a first sense.')
bullet('<b>Browser resource availability:</b> export the genuine WordNet inventory once and bundle it locally, avoiding runtime API keys or downloads.')
bullet('<b>Implementation consistency:</b> verify the JavaScript engine against independent Python reference results.')
bullet('<b>Scope and interpretation:</b> clearly show the supported noun targets and label overlap scores as evidence, not confidence.')
h('Conclusion')
p('Sense Atlas completes the required WordNet-based WSD pipeline with a polished frontend and reproducible outputs. It identifies noun senses, exposes lexical relations and explains sentence-level results. Its key limitations are restricted target vocabulary, exact lexical overlap, absent lemmatization and negation handling, and a small educational evaluation set. Future work could add broader vocabulary, independent contextual evaluation, part-of-speech filtering and contextual embeddings.')
page()

h('Project Repository (GitHub Link)')
p('<link href="https://github.com/moulyad04/Word-Sense-Disambiguation" color="#245882">https://github.com/moulyad04/Word-Sense-Disambiguation</link>')
table(['Field','Value'],[['Repository','moulyad04/Word-Sense-Disambiguation'],['Submission branch','main'],['Contents','Frontend, Python reference pipeline, WordNet-derived inventory, sample annotations, results, tests, README and screenshots'],['PDF report','Delivered separately; excluded from GitHub per user preference']],[145,335])
p('<b>Run the finished website</b> (Python 3.11 or later; no NLP installation required):')
story.append(Preformatted('python -m http.server 8785 --bind 127.0.0.1 --directory dist\n# Open http://127.0.0.1:8785 in a browser',CODE))
p('<b>Rebuild resources and verify:</b>')
story.append(Preformatted('python -m pip install -r requirements.txt\npython -m nltk.downloader -d data/nltk_data wordnet\npython tools/build_data.py\npython -m unittest discover -s tests -v\nnode tests/verify_browser_algorithm.cjs',CODE))
p('The README includes setup, scope, deliverable mapping and reproducibility details. To regenerate this PDF, install requirements-report.txt and run python tools/build_report.py. Student name and USN are left blank for completion.')
h('References')
bullet('Princeton University. WordNet 3.0 lexical database. <link href="https://wordnet.princeton.edu/" color="#245882">wordnet.princeton.edu</link>. Definitions and lexical relations are redistributed with the original WordNet license.')
bullet('NLTK Project. WordNet interface documentation. <link href="https://www.nltk.org/howto/wordnet.html" color="#245882">nltk.org/howto/wordnet.html</link>. Corpus access and synset relation APIs.')
bullet('NLTK Project. nltk.wsd / Lesk documentation. <link href="https://www.nltk.org/api/nltk.wsd.html" color="#245882">nltk.org/api/nltk.wsd.html</link>. Methodological background; the submitted scoring variants are custom implementations.')
bullet('Python documentation: <link href="https://docs.python.org/3/" color="#245882">docs.python.org/3</link>. Regular expressions, CSV handling, unittest and local HTTP serving.')
p('The sample sentence collection and application code were prepared for this exercise. The supplied lab manual defines the task, and the supplied Lab 1 sample defines this report format. No external LLM API or copied pretrained model is used.')
page()

story.append(Paragraph('ADVANCE NLP (AML23702)<br/>LAB EXERCISE EVALUATION SHEET',TITLE))
table(['Student details','Value'],[['Student Name','MOULYA D'],['USN','1GA23AI026'],['Lab Exercise No.','5'],['Experiment Title','Word Sense Disambiguation using WordNet - Sense Atlas']],[145,335])
h('Marks Awarded')
criteria=[('Problem Understanding & Scope','5'),('Pipeline Design & Methodology','10'),('Implementation Correctness','10'),('Use of NLP Tools / Models','5'),('Output Quality / Task Performance','10'),('Analysis & Interpretation','5'),('Documentation & Deliverables','2.5'),('Presentation & Reproducibility','2.5')]
table(['Sl. No.','Evaluation Criteria','Max Marks','Marks Obtained'],[[i+1,c,m,''] for i,(c,m) in enumerate(criteria)]+[['','Total','50','']],[45,260,75,100])
h('Overall Comments')
story.append(Spacer(1,65))
table(['Date of Submission','Signature of Faculty'],[['','']],[240,240])

class NumberedCanvas(Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.saved=[]
    def showPage(self):self.saved.append(dict(self.__dict__));self._startPage()
    def save(self):
        total=len(self.saved)
        for state in self.saved:
            self.__dict__.update(state)
            self.setFont('Times-Italic',9);self.setFillColor(colors.grey)
            self.drawString(54,756,'Department of AIML');self.drawRightString(558,756,'Advance NLP (AML23702)')
            self.setStrokeColor(colors.HexColor('#bbbbbb'));self.setLineWidth(.4);self.line(54,749,558,749)
            self.setFont('Times-Roman',9);self.drawCentredString(306,32,f'Page {self._pageNumber} of {total}')
            super().showPage()
        super().save()

if __name__=='__main__':
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(OUTPUT),pagesize=(612,792),rightMargin=66,leftMargin=66,topMargin=60,bottomMargin=55,title='Lab Exercise 5 - Word Sense Disambiguation',author='Department of AIML')
    doc.build(story,canvasmaker=NumberedCanvas)
    print(OUTPUT)
