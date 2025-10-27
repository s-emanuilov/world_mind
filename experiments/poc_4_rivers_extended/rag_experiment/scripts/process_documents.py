#!/usr/bin/env python3
"""
Document Processing and Chunking for RAG Experiment
Processes river documents from CSV and creates chunks for embedding.
"""

import csv
import json
import os
import re
from typing import List, Dict, Any
from configparser import ConfigParser

class DocumentProcessor:
    def __init__(self, config_path: str):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.chunk_size = self.config['chunk_size']
        self.chunk_overlap = self.config['chunk_overlap']
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or text.strip() == '':
            return ''
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def create_document_text(self, row: Dict[str, str]) -> str:
        """Create comprehensive document text from CSV row."""
        parts = []
        
        # River name
        if row.get('riverName'):
            parts.append(f"River: {row['riverName']}")
        
        # Abstract (main content)
        if row.get('abstract'):
            parts.append(f"Description: {row['abstract']}")
        
        # Geographic information
        geo_info = []
        if row.get('sourceLocation'):
            geo_info.append(f"Source: {row['sourceLocation']}")
        if row.get('sourceMountain'):
            geo_info.append(f"Source Mountain: {row['sourceMountain']}")
        if row.get('sourceState'):
            geo_info.append(f"Source State: {row['sourceState']}")
        if row.get('sourceElevation'):
            geo_info.append(f"Source Elevation: {row['sourceElevation']}")
        
        if row.get('mouthLocation'):
            geo_info.append(f"Mouth Location: {row['mouthLocation']}")
        if row.get('mouthState'):
            geo_info.append(f"Mouth State: {row['mouthState']}")
        if row.get('mouthElevation'):
            geo_info.append(f"Mouth Elevation: {row['mouthElevation']}")
        
        if geo_info:
            parts.append(f"Geographic Information: {'; '.join(geo_info)}")
        
        # Physical characteristics
        physical_info = []
        if row.get('length'):
            physical_info.append(f"Length: {row['length']} meters")
        if row.get('discharge'):
            physical_info.append(f"Discharge: {row['discharge']}")
        if row.get('watershed'):
            physical_info.append(f"Watershed: {row['watershed']}")
        
        if physical_info:
            parts.append(f"Physical Characteristics: {'; '.join(physical_info)}")
        
        # Administrative information
        admin_info = []
        if row.get('state'):
            admin_info.append(f"State: {row['state']}")
        if row.get('county'):
            admin_info.append(f"County: {row['county']}")
        if row.get('country'):
            admin_info.append(f"Country: {row['country']}")
        
        if admin_info:
            parts.append(f"Administrative Information: {'; '.join(admin_info)}")
        
        # River system and tributaries
        system_info = []
        if row.get('riverSystem'):
            system_info.append(f"River System: {row['riverSystem']}")
        if row.get('riverMouth'):
            system_info.append(f"Flows into: {row['riverMouth']}")
        if row.get('leftTributary'):
            system_info.append(f"Left Tributary: {row['leftTributary']}")
        if row.get('rightTributary'):
            system_info.append(f"Right Tributary: {row['rightTributary']}")
        
        if system_info:
            parts.append(f"River System: {'; '.join(system_info)}")
        
        # Other names
        if row.get('otherNames'):
            parts.append(f"Also known as: {row['otherNames']}")
        
        return ' '.join(parts)
    
    def chunk_text(self, text: str, river_name: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        if not text or len(text) <= self.chunk_size:
            return [{
                'text': text,
                'river_name': river_name,
                'chunk_id': f"{river_name}_chunk_0",
                'start_pos': 0,
                'end_pos': len(text)
            }]
        
        chunks = []
        start = 0
        chunk_idx = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + self.chunk_size - 100, start)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > search_start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'river_name': river_name,
                    'chunk_id': f"{river_name}_chunk_{chunk_idx}",
                    'start_pos': start,
                    'end_pos': end
                })
                chunk_idx += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_documents(self, csv_path: str) -> List[Dict[str, Any]]:
        """Process all documents from CSV file."""
        all_chunks = []
        
        print(f"Processing documents from {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_idx, row in enumerate(reader):
                if row_idx % 1000 == 0:
                    print(f"Processed {row_idx} documents...")
                
                # Create document text
                doc_text = self.create_document_text(row)
                doc_text = self.clean_text(doc_text)
                
                if not doc_text:
                    continue
                
                river_name = row.get('riverName', f'river_{row_idx}')
                
                # Create chunks
                chunks = self.chunk_text(doc_text, river_name)
                
                # Add metadata to each chunk
                for chunk in chunks:
                    chunk.update({
                        'row_index': row_idx,
                        'original_river': row.get('river', ''),
                        'wiki_page_id': row.get('wikiPageID', ''),
                        'document_length': len(doc_text)
                    })
                
                all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} chunks from {row_idx + 1} documents")
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict[str, Any]], output_path: str):
        """Save chunks to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(chunks)} chunks to {output_path}")


def main():
    """Main processing function."""
    config_path = 'config/rag_config.json'
    processor = DocumentProcessor(config_path)
    
    # Process documents
    csv_path = processor.config['data_paths']['documents']
    chunks = processor.process_documents(csv_path)
    
    # Save chunks
    output_path = processor.config['output_paths']['chunks']
    processor.save_chunks(chunks, output_path)
    
    # Print statistics
    print(f"\nDocument Processing Statistics:")
    print(f"Total chunks: {len(chunks)}")
    print(f"Average chunk length: {sum(len(c['text']) for c in chunks) / len(chunks):.1f} characters")
    print(f"Unique rivers: {len(set(c['river_name'] for c in chunks))}")


if __name__ == "__main__":
    main()
