#!/usr/bin/env python3
"""
Graph-based retrieval for rivers Graph-RAG experiment.
Retrieves relevant subgraphs instead of text chunks.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(EXPERIMENT_DIR)))
sys.path.insert(0, PROJECT_ROOT)

from rdflib import Namespace
WM = Namespace("http://worldmind.ai/rivers-v4#")

class GraphRetrievalSystem:
    """Retrieve subgraphs from knowledge graph based on query."""
    
    def __init__(self, graph_path: str):
        """Initialize with graph path."""
        self.graph = Graph()
        self.graph.parse(graph_path, format='turtle')
        print(f"Loaded graph with {len(self.graph)} triples")
    
    def get_river_by_name(self, river_name: str) -> Optional[List[Dict]]:
        """Get all triples for a specific river by name."""
        results = []
        
        for river in self.graph.subjects(RDF.type, WM.River):
            for label in self.graph.objects(river, RDFS.label):
                if river_name.lower() in str(label).lower():
                    # Get all triples for this river
                    for s, p, o in self.graph.triples((river, None, None)):
                        results.append({
                            'subject': str(s),
                            'predicate': str(p),
                            'object': str(o)
                        })
                    return results
        
        return None
    
    def get_subgraph_for_question(self, question: str, river_name: Optional[str] = None, 
                                   max_hops: int = 3) -> tuple[List[Dict], Optional]:
        """Get relevant subgraph for a question with expanded context."""
        results = []
        main_river_uri = None
        
        # If we have a river name, start there
        if river_name:
            river_uri = None
            river_label = None
            
            # Try fuzzy matching - check for partial matches
            river_name_clean = river_name.lower().strip()
            
            # First pass: exact match  
            # Only check subjects that ARE rivers (have type WM.River)
            for subject in self.graph.subjects(RDF.type, WM.River):
                if river_uri:
                    break
                for label in self.graph.objects(subject, RDFS.label):
                    label_str = str(label)
                    # Exact match first
                    if label_str == river_name:
                        river_uri = subject
                        river_label = label_str
                        break
                if river_uri:
                    break
            
            # Second pass: substring match only if no exact match
            if not river_uri:
                for subject in self.graph.subjects(RDF.type, WM.River):
                    if river_uri:
                        break
                    for label in self.graph.objects(subject, RDFS.label):
                        label_str = str(label)
                        label_lower = label_str.lower()
                        # For names like "Abrams Creek (Tennessee)", match the first part
                        if '(' in river_name:
                            first_part = river_name_clean.split('(')[0].strip()
                            if label_lower.startswith(first_part) and '(' in label_str:
                                # Prefer matches that also have state designation
                                river_uri = subject
                                river_label = label_str
                                break
            
            # Third pass: simple substring without state requirement
            if not river_uri:
                for subject in self.graph.subjects(RDF.type, WM.River):
                    if river_uri:
                        break
                    for label in self.graph.objects(subject, RDFS.label):
                        label_lower = str(label).lower()
                        first_part = river_name_clean.split('(')[0].strip() if '(' in river_name else river_name_clean
                        if label_lower.startswith(first_part):
                            river_uri = subject
                            river_label = str(label)
                            break
            
            if river_uri:
                main_river_uri = river_uri  # Track the main river
                # Get ALL triples for this river (0 hops = river itself)
                visited = set()
                to_expand = [(river_uri, 0)]
                
                # Also add related rivers (neighbors)
                related_rivers = set()
                
                while to_expand:
                    current, hops = to_expand.pop(0)
                    
                    if current in visited or hops > max_hops:
                        continue
                    
                    visited.add(current)
                    
                    # Get all triples with this as subject
                    for s, p, o in self.graph.triples((current, None, None)):
                        results.append({
                            'subject': str(s),
                            'predicate': str(p),
                            'object': str(o),
                            'hops': hops
                        })
                        
                        # Collect related rivers
                        pred_name = str(p).split('#')[-1] if '#' in str(p) else str(p).split('/')[-1]
                        if pred_name in ['hasTributary', 'flowsInto', 'hasSource', 'hasMouth']:
                            if isinstance(o, URIRef):
                                # Check if it's another river
                                if (o, RDF.type, WM.River) in self.graph:
                                    related_rivers.add(o)
                        
                        # If object is a URI and we haven't visited it, expand
                        if isinstance(o, URIRef) and str(o) not in visited:
                            to_expand.append((o, hops + 1))
                    
                    # Get all triples with this as object
                    for s, p, o in self.graph.triples((None, None, current)):
                        results.append({
                            'subject': str(s),
                            'predicate': str(p),
                            'object': str(o),
                            'hops': hops
                        })
            
            # Add information about related rivers
            for related in related_rivers:
                # Get key facts about related rivers
                for s, p, o in self.graph.triples((related, None, None)):
                    p_name = str(p).split('#')[-1] if '#' in str(p) else str(p).split('/')[-1]
                    if p_name in ['length', 'discharge', 'sourceElevation', 'mouthElevation', 'traverses', 'hasMouth', 'hasSource', 'riverName']:
                        results.append({
                            'subject': str(s),
                            'predicate': str(p),
                            'object': str(o),
                            'hops': 10  # Mark as related river
                        })
        
        return results, main_river_uri
    
    def format_context(self, triples: List[Dict], main_river_uri=None) -> str:
        """Format triples into readable context for LLM with abstracts."""
        if not triples:
            return "No relevant graph context found."
        
        context_parts = []
        
        # Group by subject and find abstract text
        by_subject = {}
        abstracts = {}
        
        for triple in triples:
            subj = triple['subject']
            if subj not in by_subject:
                by_subject[subj] = []
            by_subject[subj].append(triple)
            
            # Collect abstract text
            pred = triple['predicate']
            if 'abstractText' in str(pred):
                if subj not in abstracts:
                    abstracts[subj] = []
                abstracts[subj].append(str(triple['object']))
        
        # Use the provided main_river_uri or try to find it
        main_river = str(main_river_uri) if main_river_uri else None
        if not main_river:
            for subject, facts in by_subject.items():
                if 'river' in subject.lower() or '/River' in subject:
                    main_river = subject
                    break
        
        if main_river and main_river in abstracts:
            context_parts.append("=== RIVER SUMMARY ===")
            for abstract in abstracts[main_river]:
                # Truncate long abstracts
                ab = abstract[:500] + "..." if len(abstract) > 500 else abstract
                context_parts.append(ab)
            context_parts.append("")
        
        context_parts.append("=== STRUCTURED FACTS ===")
        
        # Group facts by type
        fact_types = {
            'Physical Attributes': ['length', 'discharge', 'elevation'],
            'Geography': ['traverses', 'inCountry', 'inCounty'],
            'Relationships': ['hasTributary', 'flowsInto', 'hasSource', 'hasMouth', 'partOfSystem']
        }
        
        for subject, facts in sorted(by_subject.items()):
            if main_river and subject == main_river:
                context_parts.append(f"\n## Main River: {subject.split('/')[-1]}")
            elif 'River' in subject:
                continue  # Skip related rivers for now
            
            # Group by type
            for type_name, preds in fact_types.items():
                type_facts = [f for f in facts if any(p in str(f['predicate']).lower() for p in preds)]
                if type_facts:
                    context_parts.append(f"\n### {type_name}:")
                    for fact in type_facts:
                        pred = fact['predicate']
                        obj = fact['object']
                        
                        rel_name = pred.split('#')[-1] if '#' in pred else pred.split('/')[-1]
                        obj_name = obj.split('/')[-1] if '/' in obj else obj
                        
                        # Format numeric values nicely
                        if any(x in rel_name for x in ['length', 'discharge', 'elevation']):
                            if isinstance(obj, (int, float)) or (isinstance(obj, str) and obj.replace('.','').isdigit()):
                                # Try to format as number
                                try:
                                    num = float(obj)
                                    if num > 1000:
                                        obj_name = f"{num/1000:.1f} km" if 'length' in rel_name else f"{num:.0f}"
                                    else:
                                        obj_name = f"{num}"
                                except:
                                    pass
                        
                        context_parts.append(f"  - {rel_name}: {obj_name}")
        
        return "\n".join(context_parts)
    
    def retrieve_for_question(self, question: str, river_name: Optional[str] = None) -> str:
        """Retrieve graph context for a question with expanded context."""
        triples, main_river_uri = self.get_subgraph_for_question(question, river_name, max_hops=3)
        
        # If no triples found, try keyword-based search in the question
        if not triples or len(triples) < 5:
            # Try to find any river mentioned in question
            import re
            keywords = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(River|Creek|Stream)\b', question)
            for keyword, _ in keywords[:2]:  # Try first 2 matches
                alt_triples, _ = self.get_subgraph_for_question(question, keyword, max_hops=3)
                if alt_triples:
                    triples.extend(alt_triples)
        
        return self.format_context(triples, main_river_uri)
