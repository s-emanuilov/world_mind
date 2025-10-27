#!/usr/bin/env python3
"""
Retrieval System for RAG Experiment
Implements similarity search and document retrieval for RAG pipeline.
"""

import json
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from typing import List, Dict, Any, Tuple
import os
from sklearn.metrics.pairwise import cosine_similarity

class RetrievalSystem:
    def __init__(self, config_path: str):
        """Initialize retrieval system."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.model_name = self.config['embedding_model']
        self.max_tokens = self.config['max_tokens']
        self.task_instruction = self.config['task_instruction']
        self.top_k = self.config['retrieval_top_k']
        self.similarity_threshold = self.config['similarity_threshold']
        
        # Load model and tokenizer
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Set device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        # Load embeddings and metadata
        self.load_embeddings_and_metadata()
        
        print(f"Retrieval system initialized on device: {self.device}")
        print(f"Loaded {len(self.chunks)} document chunks")
    
    def load_embeddings_and_metadata(self):
        """Load pre-computed embeddings and chunk metadata."""
        embeddings_path = self.config['output_paths']['embeddings']
        metadata_path = self.config['output_paths']['metadata']
        
        # Load embeddings
        self.chunk_embeddings = np.load(embeddings_path)
        print(f"Loaded chunk embeddings: {self.chunk_embeddings.shape}")
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            self.chunks = json.load(f)
        
        print(f"Loaded {len(self.chunks)} chunk metadata entries")
    
    def average_pool(self, last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """Average pooling for embeddings."""
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
    
    def get_detailed_instruct(self, task_description: str, query: str) -> str:
        """Format instruction for query embedding."""
        return f'Instruct: {task_description}\nQuery: {query}'
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        # Add instruction
        instructed_query = self.get_detailed_instruct(self.task_instruction, query)
        
        # Tokenize
        batch_dict = self.tokenizer(
            [instructed_query], 
            max_length=self.max_tokens, 
            padding=True, 
            truncation=True, 
            return_tensors='pt'
        )
        
        # Move to device
        batch_dict = {k: v.to(self.device) for k, v in batch_dict.items()}
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**batch_dict)
            embedding = self.average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
            
            # Normalize embedding
            embedding = F.normalize(embedding, p=2, dim=1)
        
        return embedding.cpu().numpy()
    
    def retrieve_documents(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Retrieve most relevant documents for a query."""
        if top_k is None:
            top_k = self.top_k
        
        # Generate query embedding
        query_embedding = self.embed_query(query)
        
        # Compute similarities
        similarities = cosine_similarity(query_embedding, self.chunk_embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filter by similarity threshold
        filtered_indices = [idx for idx in top_indices if similarities[idx] >= self.similarity_threshold]
        
        # Prepare results
        results = []
        for idx in filtered_indices:
            chunk = self.chunks[idx].copy()
            chunk['similarity_score'] = float(similarities[idx])
            chunk['rank'] = len(results) + 1
            results.append(chunk)
        
        return results
    
    def retrieve_for_question(self, question: str, river_name: str = None) -> List[Dict[str, Any]]:
        """Retrieve documents for a specific question, optionally filtering by river name."""
        # Retrieve documents
        results = self.retrieve_documents(question)
        
        # Filter by river name if provided
        if river_name:
            filtered_results = []
            for result in results:
                if river_name.lower() in result['river_name'].lower():
                    filtered_results.append(result)
            
            # If no river-specific results, fall back to general results
            if not filtered_results:
                print(f"No specific results for river '{river_name}', using general results")
                return results[:self.top_k]
            
            return filtered_results[:self.top_k]
        
        return results[:self.top_k]
    
    def get_context_for_question(self, question: str, river_name: str = None) -> str:
        """Get formatted context for a question."""
        results = self.retrieve_for_question(question, river_name)
        
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"Context {i} (Similarity: {result['similarity_score']:.3f}):\n{result['text']}\n")
        
        return "\n".join(context_parts)
    
    def evaluate_retrieval_quality(self, question: str, expected_river: str) -> Dict[str, Any]:
        """Evaluate retrieval quality for a specific question."""
        results = self.retrieve_documents(question, top_k=10)
        
        # Check if expected river is in top results
        river_found = False
        river_rank = None
        river_similarity = None
        
        for result in results:
            if expected_river.lower() in result['river_name'].lower():
                river_found = True
                river_rank = result['rank']
                river_similarity = result['similarity_score']
                break
        
        return {
            'question': question,
            'expected_river': expected_river,
            'river_found': river_found,
            'river_rank': river_rank,
            'river_similarity': river_similarity,
            'top_similarity': results[0]['similarity_score'] if results else 0.0,
            'num_results': len(results)
        }


def main():
    """Test the retrieval system."""
    config_path = 'config/rag_config.json'
    retrieval = RetrievalSystem(config_path)
    
    # Test queries
    test_queries = [
        "What is the length of the Mississippi River?",
        "Where does the Colorado River originate?",
        "What state is the Hudson River in?",
        "What is the elevation of the source of the Rio Grande?"
    ]
    
    print("Testing retrieval system...")
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = retrieval.retrieve_documents(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['river_name']} (similarity: {result['similarity_score']:.3f})")
            print(f"     {result['text'][:100]}...")


if __name__ == "__main__":
    main()
