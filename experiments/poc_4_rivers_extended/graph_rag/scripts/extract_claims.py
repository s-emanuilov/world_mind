#!/usr/bin/env python3
"""
Extract verifiable claims from LLM answers using GLiNER.
"""

import json
import os
import sys
import argparse
from typing import List, Dict, Any, Optional

try:
    from gliner import GLiNER
    GLINER_AVAILABLE = True
except ImportError:
    GLINER_AVAILABLE = False
    print("WARNING: GLiNER not available. Install with: pip install gliner")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENT_DIR = os.path.dirname(SCRIPT_DIR)

class ClaimExtractor:
    """Extract claims from text using GLiNER."""
    
    def __init__(self):
        """Initialize GLiNER model."""
        if not GLINER_AVAILABLE:
            raise ImportError("GLiNER not available. Install with: pip install gliner")
        
        print("Loading GLiNER model...")
        self.model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
        print("Model loaded")
    
    def extract_river_claims(self, text: str, labels: List[str] = None) -> List[Dict]:
        """
        Extract river-related claims from text.
        
        Args:
            text: Text to extract from
            labels: Custom entity labels (defaults to river domain labels)
        
        Returns:
            List of extracted entities with labels and spans
        """
        if labels is None:
            labels = [
                "river", "stream", "creek", "tributary",
                "state", "county", "elevation", "length",
                "mountain", "location", "measurement"
            ]
        
        entities = self.model.predict_entities(
            text=text,
            labels=labels,
            threshold=0.5
        )
        
        return entities
    
    def extract_factual_triples(self, text: str, river_name: str = None) -> List[Dict]:
        """
        Extract structured factual triples from text.
        
        Returns triples of the form (subject, predicate, object).
        """
        # First pass: extract entities
        entities = self.extract_river_claims(text)
        
        # Group entities by type
        by_type = {}
        for entity in entities:
            label = entity.get('label', 'UNKNOWN')
            if label not in by_type:
                by_type[label] = []
            by_type[label].append(entity)
        
        # Try to form triples based on proximity and semantic patterns
        triples = []
        
        # Look for river -> property -> value patterns
        rivers = by_type.get('river', [])
        
        for river_ent in rivers:
            river_text = river_ent['text']
            
            # Try to find measurements near this river
            measurements = by_type.get('measurement', [])
            
            for meas in measurements:
                # Check if measurement is mentioned near this river
                if abs(meas['start'] - river_ent['end']) < 100:  # Within 100 chars
                    triples.append({
                        'subject': river_text,
                        'predicate': 'hasMeasurement',
                        'object': meas['text']
                    })
            
            # Try to find locations
            locations = by_type.get('location', [])
            for loc in locations:
                if abs(loc['start'] - river_ent['end']) < 100:
                    triples.append({
                        'subject': river_text,
                        'predicate': 'locatedIn',
                        'object': loc['text']
                    })
        
        return triples
    
    def format_claims_for_verification(self, triples: List[Dict], 
                                       question_id: str, answer_text: str) -> Dict:
        """Format extracted claims for verification."""
        return {
            'question_id': question_id,
            'answer_text': answer_text,
            'claims': triples,
            'extraction_method': 'GLiNER'
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input JSONL file with answers")
    parser.add_argument("--output", type=str, required=True, help="Output JSONL file for claims")
    
    args = parser.parse_args()
    
    if not GLINER_AVAILABLE:
        print("ERROR: GLiNER not available")
        sys.exit(1)
    
    extractor = ClaimExtractor()
    
    with open(args.input, 'r') as inf, open(args.output, 'w') as outf:
        for line in inf:
            data = json.loads(line)
            
            question_id = data.get('question_id', '')
            answer_text = data.get('answer', '')
            
            # Extract claims
            triples = extractor.extract_factual_triples(answer_text)
            formatted = extractor.format_claims_for_verification(
                triples, question_id, answer_text
            )
            
            outf.write(json.dumps(formatted) + '\n')
            
            if len(triples) > 0:
                print(f"{question_id}: Extracted {len(triples)} claims")


if __name__ == "__main__":
    main()
