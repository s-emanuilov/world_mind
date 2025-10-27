#!/usr/bin/env python3
"""
Embedding Generation for RAG Experiment
Generates embeddings for document chunks using multilingual-e5-large-instruct model.
"""

import json
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Any
import os
from tqdm import tqdm

class EmbeddingGenerator:
    def __init__(self, config_path: str):
        """Initialize with configuration."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.model_name = self.config['embedding_model']
        self.max_tokens = self.config['max_tokens']
        self.task_instruction = self.config['task_instruction']
        
        # Load model and tokenizer
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Set device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded on device: {self.device}")
    
    def average_pool(self, last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Average pooling for embeddings."""
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def get_detailed_instruct(self, task_description: str, query: str) -> str:
        """Format instruction for query embedding."""
        return f'Instruct: {task_description}\nQuery: {query}'
    
    def embed_texts(self, texts: List[str], is_query: bool = False) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        # Add instruction for queries
        if is_query:
            texts = [self.get_detailed_instruct(self.task_instruction, text) for text in texts]
        
        # Tokenize
        batch_dict = self.tokenizer(
            texts, 
            max_length=self.max_tokens, 
            padding=True, 
            truncation=True, 
            return_tensors='pt'
        )
        
        # Move to device
        batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.model(**batch_dict)
            embeddings = self.average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
            
            # Normalize embeddings
            embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def generate_chunk_embeddings(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for all document chunks."""
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        all_embeddings = []
        
        # Process in batches
        for i in tqdm(range(0, len(chunks), batch_size), desc="Generating embeddings"):
            batch_chunks = chunks[i:i + batch_size]
            batch_texts = [chunk['text'] for chunk in batch_chunks]
            
            # Generate embeddings (documents don't need instruction)
            batch_embeddings = self.embed_texts(batch_texts, is_query=False)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all embeddings
        embeddings = np.vstack(all_embeddings)
        print(f"Generated embeddings shape: {embeddings.shape}")
        
        return embeddings
    
    def generate_question_embeddings(self, questions: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for questions."""
        print(f"Generating embeddings for {len(questions)} questions...")
        
        all_embeddings = []
        
        # Process in batches
        for i in tqdm(range(0, len(questions), batch_size), desc="Generating question embeddings"):
            batch_questions = questions[i:i + batch_size]
            
            # Generate embeddings (questions need instruction)
            batch_embeddings = self.embed_texts(batch_questions, is_query=True)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all embeddings
        embeddings = np.vstack(all_embeddings)
        print(f"Generated question embeddings shape: {embeddings.shape}")
        
        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, output_path: str):
        """Save embeddings to numpy file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        np.save(output_path, embeddings)
        print(f"Saved embeddings to {output_path}")
    
    def save_metadata(self, metadata: List[Dict[str, Any]], output_path: str):
        """Save chunk metadata."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata to {output_path}")


def main():
    """Main embedding generation function."""
    config_path = 'config/rag_config.json'
    generator = EmbeddingGenerator(config_path)
    
    # Load chunks
    chunks_path = generator.config['output_paths']['chunks']
    with open(chunks_path, 'r') as f:
        chunks = json.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Generate embeddings for chunks
    chunk_embeddings = generator.generate_chunk_embeddings(chunks)
    
    # Save embeddings and metadata
    embeddings_path = generator.config['output_paths']['embeddings']
    generator.save_embeddings(chunk_embeddings, embeddings_path)
    
    metadata_path = generator.config['output_paths']['metadata']
    generator.save_metadata(chunks, metadata_path)
    
    print(f"\nEmbedding Generation Complete!")
    print(f"Chunk embeddings shape: {chunk_embeddings.shape}")
    print(f"Embedding dimension: {chunk_embeddings.shape[1]}")


if __name__ == "__main__":
    main()
