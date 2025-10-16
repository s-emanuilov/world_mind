"""
Extract verifiable claims from LLM answers using a fast LLM, then
ground labels to graph URIs using the knowledge graph labels.
Outputs JSONL with normalized claim triples compatible with the auditor.
"""

import json
import os
import sys
import difflib
import unicodedata
import argparse
from typing import Dict, Any, List, Optional, Tuple


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

# Allow importing sibling helper when running as a script
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from openrouter_client import OpenRouterClient

ANSWERS_IN_DEFAULT = os.path.join(EXPERIMENT_DIR, "artifacts", "llm_answers.jsonl")
CLAIMS_OUT_DEFAULT = os.path.join(EXPERIMENT_DIR, "artifacts", "llm_claims.jsonl")
GRAPH_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")

FAST_MODEL = "google/gemini-2.5-flash-lite"


WM_NS = "http://worldmind.ai/battles#"
PREDICATE = f"{WM_NS}hasCommander"

# Import rdflib lazily to avoid heavy import if not needed elsewhere
from rdflib import Graph, Namespace, RDF, RDFS
WM = Namespace(WM_NS)


EXTRACTION_SYSTEM = (
    "You extract a single claim of the form: Battle hasCommander Commander.\n"
    "You must return strict JSON with keys: battle_label, commander_label.\n"
    "Do not invent. If uncertain or absent, set both to null."
)


FEW_SHOT = (
    "Examples (output JSON only):\n"
    "Answer: 'Minamoto no Yoritomo commanded at the Battle of Ishibashiyama.'\n"
    '{"battle_label": "Battle of Ishibashiyama", "commander_label": "Minamoto no Yoritomo"}\n\n'
    "Answer: 'Henry II, Count of Champagne was at the Third Crusade.'\n"
    '{"battle_label": "Third Crusade", "commander_label": "Henry II, Count of Champagne"}\n\n'
)


def build_prompt(answer_text: str) -> List[Dict[str, str]]:
    instruction = (
        "From the following answer text, extract the battle name and commander name.\n"
        "Return JSON: {\"battle_label\": string|null, \"commander_label\": string|null}.\n"
        "Use canonical English titles without extra punctuation."
    )
    user = f"{FEW_SHOT}Answer text to extract from:\n{answer_text}"
    return [
        {"role": "system", "content": EXTRACTION_SYSTEM},
        {"role": "user", "content": instruction + "\n\n" + user},
    ]


def normalize_label(label: str) -> str:
    text = unicodedata.normalize("NFKD", label)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.strip().lower()
    return text


def build_label_indices(graph_path: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    g = Graph()
    g.parse(graph_path, format="turtle")

    battle_labels_to_uris: Dict[str, List[str]] = {}
    commander_labels_to_uris: Dict[str, List[str]] = {}

    for battle in g.subjects(RDF.type, WM.Battle):
        label = g.value(battle, RDFS.label)
        if label:
            key = normalize_label(str(label))
            battle_labels_to_uris.setdefault(key, []).append(str(battle))

    for agent in g.subjects(RDF.type, WM.Agent):
        label = g.value(agent, RDFS.label)
        if label:
            key = normalize_label(str(label))
            commander_labels_to_uris.setdefault(key, []).append(str(agent))

    return battle_labels_to_uris, commander_labels_to_uris


def link_label(label: Optional[str], index: Dict[str, List[str]]) -> Optional[str]:
    if not label:
        return None
    key = normalize_label(label)
    # Exact normalized match
    if key in index:
        return index[key][0]
    # Try simple underscore/space swaps
    variants = {key.replace("_", " "), key.replace(" ", "_")}
    for v in variants:
        if v in index:
            return index[v][0]
    # Fuzzy match
    candidates = difflib.get_close_matches(key, index.keys(), n=1, cutoff=0.85)
    if candidates:
        return index[candidates[0]][0]
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--answers", type=str, default=ANSWERS_IN_DEFAULT)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()

    answers_path = args.answers
    out_path = args.out or (
        os.path.join(
            EXPERIMENT_DIR,
            "artifacts",
            f"llm_claims_{os.path.splitext(os.path.basename(answers_path))[0].replace('.', '_')}.jsonl",
        )
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    client = OpenRouterClient()

    # Build indices from the current graph
    battles_index, commanders_index = build_label_indices(GRAPH_PATH)

    with open(answers_path, "r") as inf, open(out_path, "w") as outf:
        for line in inf:
            rec = json.loads(line)
            answer_text = rec.get("answer", "")
            messages = build_prompt(answer_text)
            resp = client.chat(
                model=FAST_MODEL,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"},
                max_tokens=256,
            )
            content = OpenRouterClient.first_text(resp)
            try:
                extracted = json.loads(content)
            except Exception:
                extracted = {"battle_label": None, "commander_label": None}

            battle_uri = link_label(extracted.get("battle_label"), battles_index)
            commander_uri = link_label(extracted.get("commander_label"), commanders_index)

            claim = {
                "subject": battle_uri,
                "predicate": PREDICATE,
                "object": commander_uri,
            }
            outf.write(json.dumps({"id": rec.get("id"), "claim": claim, "answer": answer_text}) + "\n")
            print(f"Extracted+linked for {rec.get('id')}: {claim}")
    print(f"Saved claims to {out_path}")


if __name__ == "__main__":
    main()


