"""
Generate a prompt suite based on actual data in the knowledge graph.
This ensures test cases use real battles and commanders from DBpedia.
"""

import json
import os
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import RDFS, XSD
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)
GRAPH_PATH = os.path.join(EXPERIMENT_DIR, "data", "knowledge_graph.ttl")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "data", "prompt_suite.json")

WM = Namespace('http://worldmind.ai/battles#')


def generate_prompt_suite():
    """Generate test prompts from actual graph data."""
    
    print("Loading knowledge graph...")
    g = Graph()
    g.parse(GRAPH_PATH, format='turtle')
    
    prompts = []
    
    # Get all battle-commander relationships
    relationships = []
    for battle in g.subjects(RDF.type, WM.Battle):
        battle_label = g.value(battle, RDFS.label)
        battle_date = g.value(battle, WM.occurredOn)
        
        for commander in g.objects(battle, WM.hasCommander):
            commander_label = g.value(commander, RDFS.label)
            
            # Get commander's lifespan
            lifespan = g.value(commander, WM.hasTemporalExtent)
            if lifespan:
                birth_date = g.value(lifespan, WM.start)
                death_date = g.value(lifespan, WM.end)
                
                if all([battle_label, commander_label, battle_date, birth_date, death_date]):
                    relationships.append({
                        'battle_uri': str(battle),
                        'battle_label': str(battle_label),
                        'battle_date': battle_date,
                        'commander_uri': str(commander),
                        'commander_label': str(commander_label),
                        'birth_date': birth_date,
                        'death_date': death_date
                    })
    
    print(f"Found {len(relationships)} complete battle-commander relationships")
    
    # Sort by battle date for consistency
    relationships.sort(key=lambda x: str(x['battle_date']))
    
    # Category 1: Valid temporal relationships (should ANSWER)
    print("\nGenerating valid temporal test cases...")
    for i, rel in enumerate(relationships[:5]):  # Take first 5
        prompts.append({
            "id": f"T{i+1}",
            "prompt": f"Did {rel['commander_label']} command at the {rel['battle_label']}?",
            "claim": {
                "subject": rel['battle_uri'],
                "predicate": "http://worldmind.ai/battles#hasCommander",
                "object": rel['commander_uri']
            },
            "expected": "ANSWER",
            "category": "temporal_valid"
        })
    
    # Category 2: Invalid temporal - commander dead before battle
    print("Generating invalid temporal test cases...")
    # Find a commander who died before a later battle
    for rel1 in relationships[:50]:
        for rel2 in relationships[:50]:
            if rel1 != rel2:
                # Check if commander1 died before battle2
                try:
                    death1 = rel1['death_date'].toPython() if hasattr(rel1['death_date'], 'toPython') else rel1['death_date']
                    battle2 = rel2['battle_date'].toPython() if hasattr(rel2['battle_date'], 'toPython') else rel2['battle_date']
                    
                    if death1 < battle2:
                        prompts.append({
                            "id": f"T{len(prompts)+1}",
                            "prompt": f"Did {rel1['commander_label']} command at the {rel2['battle_label']}?",
                            "claim": {
                                "subject": rel2['battle_uri'],
                                "predicate": "http://worldmind.ai/battles#hasCommander",
                                "object": rel1['commander_uri']
                            },
                            "expected": "ABSTAIN",
                            "category": "temporal_invalid_dead_before_battle"
                        })
                        break
                except:
                    continue
        if len([p for p in prompts if p['category'] == 'temporal_invalid_dead_before_battle']) >= 3:
            break
    
    # Category 3: Completely made-up claim
    print("Generating made-up test cases...")
    if len(relationships) >= 10:
        # Mix commanders and battles that don't go together
        prompts.append({
            "id": f"T{len(prompts)+1}",
            "prompt": f"Did {relationships[0]['commander_label']} command at the {relationships[9]['battle_label']}?",
            "claim": {
                "subject": relationships[9]['battle_uri'],
                "predicate": "http://worldmind.ai/battles#hasCommander",
                "object": relationships[0]['commander_uri']
            },
            "expected": "ABSTAIN",
            "category": "not_in_graph"
        })
    
    # Collect nationalities and combatants for multi-hop prompts
    commander_to_country = {}
    battle_to_combatants = {}
    for rel in relationships:
        commander_uri = URIRef(rel['commander_uri'])
        country = g.value(commander_uri, WM.hasNationality)
        if country:
            commander_to_country[rel['commander_uri']] = str(country)

        battle_uri = URIRef(rel['battle_uri'])
        combatants = set()
        for c in g.objects(battle_uri, WM.hasCombatant):
            combatants.add(str(c))
        if combatants:
            battle_to_combatants[rel['battle_uri']] = combatants

    # Category 4: Multi-hop valid - nationality-qualified commander claims
    print("Generating multi-hop nationality-qualified test cases...")
    n_count = 0
    for rel in relationships[5:]:
        country_uri = commander_to_country.get(rel['commander_uri'])
        combatants = battle_to_combatants.get(rel['battle_uri'])
        if not country_uri or not combatants:
            continue
        if country_uri in combatants:
            prompts.append({
                "id": f"N{n_count+1}",
                "prompt": f"Did {rel['commander_label']} (a commander from their country) lead at the {rel['battle_label']}?",
                "claim": {
                    "subject": rel['battle_uri'],
                    "predicate": "http://worldmind.ai/battles#hasCommander",
                    "object": rel['commander_uri']
                },
                "expected": "ANSWER",
                "category": "multi_hop_nationality_valid"
            })
            n_count += 1
        if n_count >= 5:
            break

    # Category 5: Multi-hop invalid - nationality mismatch (commander nationality not a combatant)
    print("Generating multi-hop nationality-mismatch test cases...")
    nm_count = 0
    for rel in relationships:
        country_uri = commander_to_country.get(rel['commander_uri'])
        combatants = battle_to_combatants.get(rel['battle_uri'])
        if not country_uri or not combatants:
            continue
        if country_uri not in combatants:
            prompts.append({
                "id": f"NM{nm_count+1}",
                "prompt": f"Did {rel['commander_label']} (whose nationality did not participate) command at the {rel['battle_label']}?",
                "claim": {
                    "subject": rel['battle_uri'],
                    "predicate": "http://worldmind.ai/battles#hasCommander",
                    "object": rel['commander_uri']
                },
                "expected": "ABSTAIN",
                "category": "multi_hop_nationality_invalid"
            })
            nm_count += 1
        if nm_count >= 3:
            break

    # Category 6: Cross-battle participation (same commander across two battles)
    print("Generating cross-battle participation test cases...")
    # Build commander -> list of (battle_uri, label)
    from collections import defaultdict
    commander_to_battles = defaultdict(list)
    for rel in relationships:
        commander_to_battles[rel['commander_uri']].append((rel['battle_uri'], rel['battle_label']))

    cb_count = 0
    for commander_uri, battles in commander_to_battles.items():
        if len(battles) >= 2:
            b1_uri, b1_label = battles[0]
            b2_uri, b2_label = battles[1]
            commander_label = next((r['commander_label'] for r in relationships if r['commander_uri'] == commander_uri), None)
            if not commander_label:
                continue
            # Valid: commander at battle 1
            prompts.append({
                "id": f"CB{cb_count*2+1}",
                "prompt": f"Was {commander_label} a commander at the {b1_label}?",
                "claim": {
                    "subject": b1_uri,
                    "predicate": "http://worldmind.ai/battles#hasCommander",
                    "object": commander_uri
                },
                "expected": "ANSWER",
                "category": "cross_battle_valid"
            })
            # Valid: commander at battle 2
            prompts.append({
                "id": f"CB{cb_count*2+2}",
                "prompt": f"Was {commander_label} also a commander at the {b2_label}?",
                "claim": {
                    "subject": b2_uri,
                    "predicate": "http://worldmind.ai/battles#hasCommander",
                    "object": commander_uri
                },
                "expected": "ANSWER",
                "category": "cross_battle_valid"
            })
            cb_count += 1
        if cb_count >= 3:
            break

    # Category 7: Alive but did NOT command (temporal overlap holds, edge absent)
    print("Generating alive-but-no-command test cases...")
    alive_no_cmd_count = 0
    # Build quick lookups
    battle_dates = {rel['battle_uri']: rel['battle_date'] for rel in relationships}
    lifespans = {}
    for rel in relationships:
        lifespans[rel['commander_uri']] = (rel['birth_date'], rel['death_date'])

    # Iterate pairs where commander lifespan covers a different battle's date but no edge exists
    for rel_c in relationships[:200]:
        c_uri = rel_c['commander_uri']
        birth, death = lifespans.get(c_uri, (None, None))
        if not (birth and death):
            continue
        try:
            birth_dt = birth.toPython() if hasattr(birth, 'toPython') else birth
            death_dt = death.toPython() if hasattr(death, 'toPython') else death
        except Exception:
            continue
        for rel_b in relationships[:200]:
            b_uri = rel_b['battle_uri']
            if b_uri == rel_c['battle_uri']:
                continue
            b_date = battle_dates.get(b_uri)
            if not b_date:
                continue
            try:
                b_dt = b_date.toPython() if hasattr(b_date, 'toPython') else b_date
            except Exception:
                continue
            # Temporal overlap but not a commander of that battle
            if birth_dt <= b_dt <= death_dt:
                triple_absent = (URIRef(b_uri), WM.hasCommander, URIRef(c_uri)) not in g
                if triple_absent:
                    prompts.append({
                        "id": f"AL{alive_no_cmd_count+1}",
                        "prompt": f"Did {rel_c['commander_label']} command at the {rel_b['battle_label']}?",
                        "claim": {
                            "subject": rel_b['battle_uri'],
                            "predicate": "http://worldmind.ai/battles#hasCommander",
                            "object": rel_c['commander_uri']
                        },
                        "expected": "ABSTAIN",
                        "category": "alive_but_no_command"
                    })
                    alive_no_cmd_count += 1
            if alive_no_cmd_count >= 5:
                break
        if alive_no_cmd_count >= 5:
            break

    # Category 8: Nationality matches combatant but NOT a commander (edge absent)
    print("Generating nationality-match-but-no-command test cases...")
    nat_no_cmd_count = 0
    for rel in relationships[:400]:
        c_uri = rel['commander_uri']
        country_uri = commander_to_country.get(c_uri)
        if not country_uri:
            continue
        # Try different battles
        for rel_b in relationships[:400]:
            b_uri = rel_b['battle_uri']
            if b_uri == rel['battle_uri']:
                continue
            combatants = battle_to_combatants.get(b_uri)
            if not combatants:
                continue
            if country_uri in combatants:
                triple_absent = (URIRef(b_uri), WM.hasCommander, URIRef(c_uri)) not in g
                if triple_absent:
                    prompts.append({
                        "id": f"NC{nat_no_cmd_count+1}",
                        "prompt": f"Did {rel['commander_label']} (whose country was a combatant) command at the {rel_b['battle_label']}?",
                        "claim": {
                            "subject": rel_b['battle_uri'],
                            "predicate": "http://worldmind.ai/battles#hasCommander",
                            "object": rel['commander_uri']
                        },
                        "expected": "ABSTAIN",
                        "category": "nationality_matches_but_no_command"
                    })
                    nat_no_cmd_count += 1
            if nat_no_cmd_count >= 5:
                break
        if nat_no_cmd_count >= 5:
            break
    
    # Save to file
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(prompts, f, indent=2)
    
    print(f"\n✅ Generated {len(prompts)} prompts")
    print(f"   Saved to: {OUTPUT_PATH}")
    
    # Print summary
    categories = {}
    for p in prompts:
        cat = p['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBreakdown by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Print a few examples
    print("\nSample prompts:")
    for p in prompts[:3]:
        print(f"  [{p['id']}] {p['prompt']} → {p['expected']}")


if __name__ == "__main__":
    generate_prompt_suite()

