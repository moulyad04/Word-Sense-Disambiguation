// Verify the browser algorithm matches the independent Python run for all 48 rows.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {analyze}=require('../dist/app.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../dist/assets/wordnet-data.json'),'utf8'));
for(const r of data.results){const actual=analyze(r.sentence,r.word,data.inventory,r.mode);for(const key of ['selected','status','score','margin','ranked','context'])assert.deepEqual(actual[key],r[key],`${r.id}: ${r.mode}: ${key}`);}
assert.equal(analyze('The bank is here.','bank',data.inventory).selected,null);
assert.throws(()=>analyze('Hello world','bank',data.inventory),/target word/);
assert.throws(()=>analyze('The bank','constructor',data.inventory),/supported inventory/);
console.log('PASS: 48 predictions match Python; zero-evidence and invalid-input checks passed.');
