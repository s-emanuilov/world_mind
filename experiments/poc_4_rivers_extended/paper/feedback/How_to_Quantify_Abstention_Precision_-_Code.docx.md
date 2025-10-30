Absolutely—below is a **ready-to-drop code bundle** for items **A–E**. It’s modular and minimal, with clean interfaces so you can wire your own model adapters (raw LLM, RAG, Graph-licensed oracle). I’ve included:

* **A**: context-card generator, unified evaluator, abstention metrics
* **B** *(optional but recommended)*: clause-level stream guard (in-loop gating)
* **C**: near-miss adversarial generator
* **D**: a second-domain (Cities→Mayors) mini-pipeline (graph builder, SHACL, Q&A)
* **E**: an HTML report generator that uses the abstention metrics

You can copy these into your repo preserving the folder structure shown. They assume **Python 3.10+** and **rdflib**.

Directory layout

experiments/

A\_cards\_and\_eval/

cards/

make\_context\_cards.py

eval/

run\_epistemic\_tests.py

metrics\_abstention.py

B\_stream\_gating/

gen/

stream\_guard.py

C\_adversarial/

make\_near\_miss.py

D\_cities\_domain/

build\_graph.py

cities\_shacl.ttl

make\_city\_qa.py

E\_reporting/

html\_report\_ext.py

**A) Context cards, unified evaluator, abstention metrics**

cards/make\_context\_cards.py

#!/usr/bin/env python3

"""

Generate “context cards” from a KG TTL for epistemic-confusion tests.

Card schema (JSONL):

{

"id": "CARD\_0001",

"facts": ["Escanaba River has mouth: Lake Michigan", "…", "Bear Creek DOES NOT have tributary: Whetstone River"],

"question": "Is Whetstone River a tributary of Bear Creek?",

"gold": "YES|NO|UNKNOWN",

"claim": {"subj":"IRI","pred":"IRI","obj":"IRI"},

"label": "E|C|U" # entailed / contradictory / unknown

}

"""

import argparse, json, random

from rdflib import Graph, URIRef

def get\_triples(g, p):

for s,o in g.subject\_objects(URIRef(p)):

yield (str(s), str(o))

def make\_card(facts, question, gold, label, claim):

return {

"id": f"CARD\_{random.getrandbits(32):08x}",

"facts": facts,

"question": question,

"gold": gold, # YES/NO/UNKNOWN

"label": label, # E/C/U

"claim": claim

}

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--kg", required=True, help="TTL knowledge graph")

ap.add\_argument("--pred", required=True, help="Predicate IRI (e.g., http://worldmind.ai/rivers#hasMouth)")

ap.add\_argument("--subj\_hint", default=None, help="Optional substring to filter subjects")

ap.add\_argument("--num", type=int, default=200, help="#cards per type (E/F/U/C)")

ap.add\_argument("--out", required=True)

args = ap.parse\_args()

g = Graph(); g.parse(args.kg, format="turtle")

triples = [(s,o) for s,o in get\_triples(g, args.pred) if (args.subj\_hint is None or args.subj\_hint in s)]

subs = list({s for s,\_ in triples})

objs = list({o for \_,o in triples})

rnd = random.Random(1337)

cards = []

# Helper to pretty print

def fact\_line(s,p,o):

return f"{s} {p} {o}"

def q\_line(s,p,o):

return f"Is {s} {p} {o}?"

# 1) Entailed TRUE (E) -> gold YES

for \_ in range(min(args.num, len(triples))):

s,o = rnd.choice(triples)

facts = [fact\_line(s, "has relation", o)]

cards.append(make\_card(

facts=facts,

question=q\_line(o if "Mouth" in args.pred else s, "related to", s if "Mouth" in args.pred else o),

gold="YES",

label="E",

claim={"subj": s, "pred": args.pred, "obj": o}

))

# 2) Explicitly FALSE (C) -> gold NO (negation present)

# pick true (s,o\_true) and a wrong o\_false != o\_true, and assert explicit NOT

for \_ in range(min(args.num, len(triples))):

s,o\_true = rnd.choice(triples)

o\_false = rnd.choice([x for x in objs if x != o\_true])

facts = [fact\_line(s, "has relation", o\_true),

f"{s} DOES NOT have relation: {o\_false} (not in database)"]

cards.append(make\_card(

facts=facts,

question=q\_line(s, "related to", o\_false),

gold="NO",

label="C",

claim={"subj": s, "pred": args.pred, "obj": o\_false}

))

# 3) UNKNOWN (U) -> gold UNKNOWN (no explicit negation, relation absent)

# pick s, and an object that is not in triples for that s, but do not assert "NOT"

for \_ in range(args.num):

s,\_ = rnd.choice(triples)

o\_candidates = [x for x in objs if (s,x) not in triples]

if not o\_candidates: continue

o = rnd.choice(o\_candidates)

facts = [fact\_line(s, "has relation", o2) for (s2,o2) in triples if s2 == s]

cards.append(make\_card(

facts=facts,

question=q\_line(s, "related to", o),

gold="UNKNOWN",

label="U",

claim={"subj": s, "pred": args.pred, "obj": o}

))

# 4) Coherence/distractor (C) -> gold NO

# ask a hydrologically plausible but wrong relation by mixing neighbors

for \_ in range(args.num):

s1,o1 = rnd.choice(triples); s2,o2 = rnd.choice(triples)

if s1 == s2: continue

# distract with true relations for both, then query wrong pair (s1,o2)

facts = [fact\_line(s1, "has relation", o1),

fact\_line(s2, "has relation", o2)]

cards.append(make\_card(

facts=facts,

question=q\_line(s1, "related to", o2),

gold="NO",

label="C",

claim={"subj": s1, "pred": args.pred, "obj": o2}

))

with open(args.out, "w", encoding="utf-8") as f:

for c in cards:

f.write(json.dumps(c, ensure\_ascii=False) + "\n")

print(f"Wrote {len(cards)} cards to {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

eval/run\_epistemic\_tests.py

#!/usr/bin/env python3

"""

Unified evaluator for the epistemic-confusion cards.

Pluggable back-ends:

- RawLLMAdapter: user wires to an API (returns YES/NO/UNKNOWN from JSON)

- RAGAdapter: same interface, but builds a prompt with retrieved context

- KGOracleAdapter: deterministic licensing gate using the KG

Outputs JSONL with per-card results.

Result row:

{

"id": "CARD\_xxx",

"gold": "YES|NO|UNKNOWN",

"pred": "YES|NO|UNKNOWN",

"pass": true/false,

"system": "raw|rag|kg\_licensed"

}

"""

import argparse, json

from typing import Dict

# ------- Adapters (wire your own) -------

class BaseAdapter:

def answer(self, card: Dict) -> str:

raise NotImplementedError

class KGOracleAdapter(BaseAdapter):

"""Deterministic: respects explicit negations in 'facts',

otherwise answers YES only when the entailed fact is present; UNKNOWN if absent."""

def \_\_init\_\_(self, pred\_phrase: str = "has relation"):

self.pred\_phrase = pred\_phrase

def answer(self, card: Dict) -> str:

s = card["claim"]["subj"]; o = card["claim"]["obj"]

has\_line = f"{s} {self.pred\_phrase} {o}"

not\_line = f"{s} DOES NOT have relation: {o}"

facts = card["facts"]

if any(not\_line in ln for ln in facts):

return "NO"

if any(has\_line in ln for ln in facts):

return "YES"

return "UNKNOWN"

class RawLLMAdapter(BaseAdapter):

"""Stub; replace with real LLM call. Always returns UNKNOWN to be conservative."""

def answer(self, card: Dict) -> str:

return "UNKNOWN"

class RAGAdapter(BaseAdapter):

"""Stub; replace with your RAG client. Defaults to UNKNOWN."""

def answer(self, card: Dict) -> str:

return "UNKNOWN"

# ------- Evaluation -------

def eval\_cards(cards\_path: str, adapter: BaseAdapter, system\_name: str, out\_path: str):

out = []

with open(cards\_path, "r", encoding="utf-8") as f:

for line in f:

card = json.loads(line)

pred = adapter.answer(card)

gold = card["gold"]

ok = (pred == gold)

out.append({"id": card["id"], "gold": gold, "pred": pred, "pass": ok, "system": system\_name})

with open(out\_path, "w", encoding="utf-8") as f:

for r in out:

f.write(json.dumps(r) + "\n")

print(f"Wrote {len(out)} results to {out\_path}")

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--cards", required=True)

ap.add\_argument("--system", choices=["raw","rag","kg"], required=True)

ap.add\_argument("--out", required=True)

args = ap.parse\_args()

if args.system == "kg":

adapter = KGOracleAdapter()

elif args.system == "raw":

adapter = RawLLMAdapter()

else:

adapter = RAGAdapter()

eval\_cards(args.cards, adapter, args.system, args.out)

if \_\_name\_\_ == "\_\_main\_\_":

main()

eval/metrics\_abstention.py

#!/usr/bin/env python3

"""

Compute abstention metrics from a combined result JSONL

(merge multiple system runs if needed beforehand).

We expect rows with keys: id, gold (YES|NO|UNKNOWN), pred (YES|NO|UNKNOWN), system.

Metrics:

- AP (Abstention Precision) overall and by type

- AR (Abstention Recall) overall and by type

- CVRR (Constraint Violation Rejection Rate) = S\_C / (S\_C + A\_C)

- FAR-NE (False Answer Rate on Non-Entailed) = (A\_C + A\_U) / all non-entailed decisions

- LA (Licensed Answer Accuracy on E) = A\_E / (A\_E + S\_E)

"""

import argparse, json, collections

def compute(rows):

# Tally by system

out\_by\_sys = {}

for sys in set(r["system"] for r in rows):

R = [r for r in rows if r["system"] == sys]

# Map gold → E/C/U via equivalence (YES==E, NO==C, UNKNOWN==U) for card gold

# If you keep a separate 'label' field in cards, switch to that instead of gold->label mapping.

# Here we assume cards.gold encodes expected epistemic outcome per the generator.

counts = collections.Counter()

for r in R:

gold = r["gold"] # YES/NO/UNKNOWN

pred = r["pred"]

# Convert: gold YES→E, NO→C, UNKNOWN→U

if gold == "YES": lab="E"

elif gold == "NO": lab="C"

else: lab="U"

if pred == "UNKNOWN": act = "S" # abstain

else: act = "A" # answer YES/NO

key = f"{act}\_{lab}"

counts[key] += 1

A\_E, A\_C, A\_U = counts["A\_E"], counts["A\_C"], counts["A\_U"]

S\_E, S\_C, S\_U = counts["S\_E"], counts["S\_C"], counts["S\_U"]

non\_entailed = (A\_C + S\_C + A\_U + S\_U)

# Metrics

AP = (S\_C + S\_U) / (S\_E + S\_C + S\_U) if (S\_E + S\_C + S\_U) else None

AP\_invalid = S\_C / (S\_C + S\_E) if (S\_C + S\_E) else None

AP\_unknown = S\_U / (S\_U + S\_E) if (S\_U + S\_E) else None

AR = (S\_C + S\_U) / non\_entailed if non\_entailed else None

CVRR = S\_C / (S\_C + A\_C) if (S\_C + A\_C) else None

FAR\_NE = (A\_C + A\_U) / non\_entailed if non\_entailed else None

LA = A\_E / (A\_E + S\_E) if (A\_E + S\_E) else None

out\_by\_sys[sys] = {

"counts": counts,

"AP": AP, "AP\_invalid": AP\_invalid, "AP\_unknown": AP\_unknown,

"AR": AR, "CVRR": CVRR, "FAR\_NE": FAR\_NE, "LA": LA

}

return out\_by\_sys

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--results", required=True, help="JSONL of per-card results with fields id,gold,pred,system")

ap.add\_argument("--out", required=True)

args = ap.parse\_args()

rows = []

with open(args.results, "r", encoding="utf-8") as f:

for line in f:

rows.append(json.loads(line))

metrics = compute(rows)

with open(args.out, "w", encoding="utf-8") as f:

json.dump(metrics, f, indent=2)

print(f"Wrote metrics to {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

**B) Clause-level “in-loop” gating (optional but powerful)**

gen/stream\_guard.py

#!/usr/bin/env python3

"""

Clause-level stream guard:

Wrap a token/segment generator; at each clause boundary, call a claim detector + licensing oracle.

If unlicensed, emit "<ABSTAIN>" and stop. Otherwise continue streaming.

Integrate by wrapping your LLM streaming client:

for segment in guard.stream(prompt):

yield segment

"""

from typing import Callable, Iterable, Dict

class StreamGuard:

def \_\_init\_\_(self,

segment\_generator: Callable[[str], Iterable[str]],

extract\_claims: Callable[[str], Dict],

is\_licensed: Callable[[Dict], bool],

clause\_delims=(".","?","!")):

self.segment\_generator = segment\_generator

self.extract\_claims = extract\_claims

self.is\_licensed = is\_licensed

self.delims = clause\_delims

def stream(self, prompt: str) -> Iterable[str]:

buffer = ""

for seg in self.segment\_generator(prompt):

buffer += seg

yield seg

# clause boundary detection (simple heuristic)

if any(buffer.endswith(d) for d in self.delims):

claim = self.extract\_claims(buffer)

if claim:

if not self.is\_licensed(claim):

yield " <ABSTAIN>"

break

Plug your existing claim extractor (e.g., GLiNER-based subject/predicate/object) and your KG is\_licensed(claim) function.

**C) Near-miss adversarial generator**

C\_adversarial/make\_near\_miss.py

#!/usr/bin/env python3

"""

Generate near-miss negatives by pairing each subject with a plausible but incorrect object.

Outputs JSONL cards with gold="NO" and label="C".

"""

import argparse, json, random

from rdflib import Graph, URIRef

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--kg", required=True)

ap.add\_argument("--pred", required=True)

ap.add\_argument("--out", required=True)

ap.add\_argument("--num", type=int, default=500)

args = ap.parse\_args()

g = Graph(); g.parse(args.kg, format="turtle")

P = URIRef(args.pred)

triples = [(str(s),str(o)) for s,o in g.subject\_objects(P)]

subs = list({s for s,\_ in triples})

objs = list({o for \_,o in triples})

rnd = random.Random(2027)

cards = []

for \_ in range(min(args.num, len(triples))):

s,o\_true = rnd.choice(triples)

o\_false = rnd.choice([x for x in objs if x != o\_true])

facts = [f"{s} has relation {o\_true}"] # state the true relation for distraction

question = f"Is {s} related to {o\_false}?"

cards.append({

"id": f"NEG\_{rnd.getrandbits(32):08x}",

"facts": facts,

"question": question,

"gold": "NO",

"label": "C",

"claim": {"subj": s, "pred": args.pred, "obj": o\_false}

})

with open(args.out, "w", encoding="utf-8") as f:

for c in cards:

f.write(json.dumps(c, ensure\_ascii=False) + "\n")

print(f"Wrote {len(cards)} near-miss cards to {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

**D) Second domain (Cities → Mayors) mini-pipeline**

D\_cities\_domain/build\_graph.py

#!/usr/bin/env python3

"""

Build a tiny Cities→Mayors knowledge graph (TTL) from a CSV:

CSV columns: city\_name, mayor\_name, country, state

Outputs:

- cities\_graph.ttl (RDF triples)

"""

import argparse, csv

from rdflib import Graph, Namespace, URIRef, Literal

from rdflib.namespace import RDF, RDFS

WM = Namespace("http://worldmind.ai/core#")

C = Namespace("http://worldmind.ai/cities#")

ENT = "http://worldmind.ai/entity/"

def IRI(label): return URIRef(ENT + label.strip().replace(" ","\_"))

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--csv", required=True)

ap.add\_argument("--out", required=True)

args = ap.parse\_args()

g = Graph()

# Minimal classes

g.add((C.City, RDF.type, RDFS.Class))

g.add((C.Person, RDF.type, RDFS.Class))

g.add((C.hasMayor, RDF.type, RDF.Property))

g.add((C.locatedIn, RDF.type, RDF.Property))

with open(args.csv, newline="", encoding="utf-8") as f:

for row in csv.DictReader(f):

city = IRI(row["city\_name"])

mayor = IRI(row["mayor\_name"])

country = IRI(row.get("country",""))

state = IRI(row.get("state",""))

g.add((city, RDF.type, C.City))

g.add((mayor, RDF.type, C.Person))

g.add((city, C.hasMayor, mayor))

if row.get("country"):

g.add((city, C.locatedIn, country))

if row.get("state"):

g.add((city, C.locatedIn, state))

g.serialize(destination=args.out, format="turtle")

print(f"Wrote {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

D\_cities\_domain/cities\_shacl.ttl

@prefix sh: <http://www.w3.org/ns/shacl#> .

@prefix c: <http://worldmind.ai/cities#> .

@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# hasMayor: domain City, range Person

c:HasMayorShape a sh:NodeShape ;

sh:targetSubjectsOf c:hasMayor ;

sh:property [

sh:path c:hasMayor ;

sh:class c:Person ;

] ;

sh:message "c:hasMayor must link City → Person." .

# Optional uniqueness: a City should have at most one mayor (illustrative; soft check)

c:UniqueMayorShape a sh:NodeShape ;

sh:targetSubjectsOf c:hasMayor ;

sh:sparql [

sh:message "City has multiple distinct mayors." ;

sh:select """

PREFIX c: <http://worldmind.ai/cities#>

SELECT ?this WHERE {

?this c:hasMayor ?m1, ?m2 .

FILTER(?m1 != ?m2)

}

""" ;

] .

D\_cities\_domain/make\_city\_qa.py

#!/usr/bin/env python3

"""

Make a simple Q&A set for Cities→Mayors:

- YES: entailed (City hasMayor Person)

- NO: wrong person (explicitly negated variant optional)

- UNKNOWN: absent person (no assertion, no negation)

Outputs JSONL cards identical to rivers format.

"""

import argparse, json, random

from rdflib import Graph, URIRef

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--kg", required=True)

ap.add\_argument("--pred", default="http://worldmind.ai/cities#hasMayor")

ap.add\_argument("--out", required=True)

ap.add\_argument("--num", type=int, default=500)

args = ap.parse\_args()

g = Graph(); g.parse(args.kg, format="turtle")

P = URIRef(args.pred)

triples = [(str(s), str(o)) for s,o in g.subject\_objects(P)]

cities = list({s for s,\_ in triples})

persons = list({o for \_,o in triples})

rnd = random.Random(77)

cards=[]

# YES

for \_ in range(min(args.num, len(triples))):

s,o = rnd.choice(triples)

facts=[f"{s} has mayor {o}"]

q=f"Is {o} the mayor of {s}?"

cards.append({"id":f"CITY\_Y\_{rnd.getrandbits(32):08x}","facts":facts,"question":q,"gold":"YES","label":"E","claim":{"subj":s,"pred":args.pred,"obj":o}})

# NO

for \_ in range(min(args.num, len(triples))):

s,o\_true = rnd.choice(triples)

o\_false = rnd.choice([p for p in persons if p != o\_true])

facts=[f"{s} has mayor {o\_true}", f"{s} DOES NOT have mayor: {o\_false}"]

q=f"Is {o\_false} the mayor of {s}?"

cards.append({"id":f"CITY\_N\_{rnd.getrandbits(32):08x}","facts":facts,"question":q,"gold":"NO","label":"C","claim":{"subj":s,"pred":args.pred,"obj":o\_false}})

# UNKNOWN

for \_ in range(args.num):

s,\_ = rnd.choice(triples)

o\_unk = rnd.choice([p for p in persons if (s,p) not in triples])

facts=[f"{s} has mayor {o\_true}" for (ss,o\_true) in triples if ss==s]

q=f"Is {o\_unk} the mayor of {s}?"

cards.append({"id":f"CITY\_U\_{rnd.getrandbits(32):08x}","facts":facts,"question":q,"gold":"UNKNOWN","label":"U","claim":{"subj":s,"pred":args.pred,"obj":o\_unk}})

with open(args.out,"w",encoding="utf-8") as f:

for c in cards:

f.write(json.dumps(c,ensure\_ascii=False)+"\n")

print(f"Wrote {len(cards)} city cards to {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

**E) HTML report (abstention metrics)**

E\_reporting/html\_report\_ext.py

#!/usr/bin/env python3

"""

Generate an extended HTML report from:

- results.jsonl (merged runs: raw/rag/kg)

- metrics.json (from metrics\_abstention.py)

Outputs report\_ext.html with tables for AP/CVRR/FAR-NE/LA and per-system counts.

"""

import argparse, json, os

def load\_json(path):

if not path or not os.path.exists(path): return None

with open(path, "r", encoding="utf-8") as f: return json.load(f)

def load\_jsonl(path):

rows=[]

with open(path,"r",encoding="utf-8") as f:

for line in f: rows.append(json.loads(line))

return rows

def main():

ap = argparse.ArgumentParser()

ap.add\_argument("--results", required=True) # merged JSONL across systems

ap.add\_argument("--metrics", required=True)

ap.add\_argument("--out", default="report\_ext.html")

args = ap.parse\_args()

rows = load\_jsonl(args.results)

metrics = load\_json(args.metrics)

systems = sorted(set(r["system"] for r in rows))

html=[]

html += ["<!doctype html><html><head><meta charset='utf-8'>",

"<title>WorldMind – Abstention Metrics</title>",

"<style>body{font-family:system-ui;margin:2rem} table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:.4rem .6rem}</style>",

"</head><body>",

"<h1>WorldMind – Abstention Metrics</h1>"]

# Metrics summary

html += ["<h2>Summary Metrics</h2>"]

html += ["<table><tr><th>System</th><th>AP</th><th>AP\_invalid</th><th>AP\_unknown</th><th>CVRR</th><th>FAR-NE</th><th>LA</th></tr>"]

for sys in systems:

m = metrics.get(sys, {})

def fmt(x): return "—" if x is None else f"{x:.3f}"

html += [f"<tr><td>{sys}</td><td>{fmt(m.get('AP'))}</td><td>{fmt(m.get('AP\_invalid'))}</td>"

f"<td>{fmt(m.get('AP\_unknown'))}</td><td>{fmt(m.get('CVRR'))}</td>"

f"<td>{fmt(m.get('FAR\_NE'))}</td><td>{fmt(m.get('LA'))}</td></tr>"]

html += ["</table>"]

# Counts per system

html += ["<h2>Counts</h2><table><tr><th>System</th><th>A\_E</th><th>A\_C</th><th>A\_U</th><th>S\_E</th><th>S\_C</th><th>S\_U</th></tr>"]

for sys in systems:

c = metrics.get(sys, {}).get("counts", {})

html += [f"<tr><td>{sys}</td><td>{c.get('A\_E',0)}</td><td>{c.get('A\_C',0)}</td><td>{c.get('A\_U',0)}</td>"

f"<td>{c.get('S\_E',0)}</td><td>{c.get('S\_C',0)}</td><td>{c.get('S\_U',0)}</td></tr>"]

html += ["</table>"]

# Raw rows (optional)

html += ["<h2>Per-card Results (sample)</h2><table><tr><th>ID</th><th>System</th><th>Gold</th><th>Pred</th><th>Pass</th></tr>"]

for r in rows[:300]:

html += [f"<tr><td>{r['id']}</td><td>{r['system']}</td><td>{r['gold']}</td><td>{r['pred']}</td><td>{'✅' if r.get('pass') else '❌'}</td></tr>"]

html += ["</table>"]

html += ["</body></html>"]

with open(args.out, "w", encoding="utf-8") as f:

f.write("".join(html))

print(f"Wrote {args.out}")

if \_\_name\_\_ == "\_\_main\_\_":

main()

**🛠️ How to run (minimal path)**

1. **Generate cards** (rivers):

python experiments/A\_cards\_and\_eval/cards/make\_context\_cards.py \

--kg data/knowledge\_graph.ttl \

--pred http://worldmind.ai/rivers#hasMouth \

--num 300 \

--out rivers\_cards.jsonl

**2. Evaluate** (start with KG-licensed stub, then plug raw/RAG adapters):

python experiments/A\_cards\_and\_eval/eval/run\_epistemic\_tests.py \

--cards rivers\_cards.jsonl --system kg --out kg\_results.jsonl

# (after wiring your LLM and RAG adapters)

python ... --system raw --out raw\_results.jsonl

python ... --system rag --out rag\_results.jsonl

# merge

cat kg\_results.jsonl raw\_results.jsonl rag\_results.jsonl > all\_results.jsonl

1. **Metrics**:

python experiments/A\_cards\_and\_eval/eval/metrics\_abstention.py \

--results all\_results.jsonl \

--out abstention\_metrics.json

1. **HTML report**:

python experiments/E\_reporting/html\_report\_ext.py \

--results all\_results.jsonl \

--metrics abstention\_metrics.json \

--out report\_ext.html

1. *(Optional)* **Near-miss adversarials**:

python experiments/C\_adversarial/make\_near\_miss.py \

--kg data/knowledge\_graph.ttl \

--pred http://worldmind.ai/rivers#hasMouth \

--out near\_miss.jsonl

1. *(Optional)* **Cities → Mayors** mini-domain:

python experiments/D\_cities\_domain/build\_graph.py \

--csv data/cities\_mayors.csv \

--out data/cities\_graph.ttl

python experiments/D\_cities\_domain/make\_city\_qa.py \

--kg data/cities\_graph.ttl \

--out city\_cards.jsonl

1. *(Optional)* **In-loop gating**: wrap your streaming LLM client with StreamGuard.

**Notes**

* The evaluator stubs for **RawLLMAdapter** and **RAGAdapter** are left minimalist on purpose; wire them to your inference endpoints to return YES|NO|UNKNOWN per the JSON schema.
* If your cards include an explicit label field (E/C/U), you can use that in metrics\_abstention.py instead of mapping from gold.
* Clause-level gating is intentionally heuristic (period/!/?). Replace extract\_claims(buffer) with your GLiNER-based triplet extractor and the is\_licensed() callback with your SHACL/ASK oracle.