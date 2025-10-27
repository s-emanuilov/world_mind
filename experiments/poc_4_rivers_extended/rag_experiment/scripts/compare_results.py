#!/usr/bin/env python3
"""
Comparison Analysis for RAG vs Direct LLM Evaluation
Compares RAG performance with direct LLM evaluation results.
"""

import json
import csv
import os
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

class ComparisonAnalyzer:
    def __init__(self, config_path: str):
        """Initialize comparison analyzer."""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.results_dir = "results"
        self.output_dir = "results/analysis"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_direct_results(self, model_name: str) -> Dict[str, Any]:
        """Load direct LLM evaluation results."""
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        results_file = f"../../evaluation/{safe_model_name}_results.jsonl"
        summary_file = f"../../evaluation/{safe_model_name}_summary.json"
        
        # Load summary
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        # Load individual results
        results = {}
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        results[data['question_id']] = data
        
        return {
            'summary': summary,
            'results': results
        }
    
    def load_rag_results(self, model_name: str) -> Dict[str, Any]:
        """Load RAG evaluation results."""
        safe_model_name = model_name.replace("/", "_").replace("\\", "_")
        results_file = f"{self.results_dir}/rag_{safe_model_name}_results.jsonl"
        summary_file = f"{self.results_dir}/rag_{safe_model_name}_summary.json"
        
        # Load summary
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        # Load individual results
        results = {}
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        results[data['question_id']] = data
        
        return {
            'summary': summary,
            'results': results
        }
    
    def compare_results(self, model_name: str) -> Dict[str, Any]:
        """Compare RAG vs Direct LLM results."""
        print(f"Loading results for {model_name}...")
        
        # Load both result sets
        direct_results = self.load_direct_results(model_name)
        rag_results = self.load_rag_results(model_name)
        
        # Get common questions
        direct_questions = set(direct_results['results'].keys())
        rag_questions = set(rag_results['results'].keys())
        common_questions = direct_questions.intersection(rag_questions)
        
        print(f"Direct LLM questions: {len(direct_questions)}")
        print(f"RAG questions: {len(rag_questions)}")
        print(f"Common questions: {len(common_questions)}")
        
        # Compare accuracy
        direct_correct = sum(1 for qid in common_questions if direct_results['results'][qid]['is_correct'])
        rag_correct = sum(1 for qid in common_questions if rag_results['results'][qid]['is_correct'])
        
        direct_accuracy = direct_correct / len(common_questions) if common_questions else 0
        rag_accuracy = rag_correct / len(common_questions) if common_questions else 0
        
        # Analyze agreement
        agreement = 0
        rag_improvements = 0
        direct_improvements = 0
        
        for qid in common_questions:
            direct_correct = direct_results['results'][qid]['is_correct']
            rag_correct = rag_results['results'][qid]['is_correct']
            
            if direct_correct == rag_correct:
                agreement += 1
            elif rag_correct and not direct_correct:
                rag_improvements += 1
            elif direct_correct and not rag_correct:
                direct_improvements += 1
        
        # Analyze retrieval quality
        retrieval_analysis = self.analyze_retrieval_quality(rag_results['results'])
        
        comparison = {
            'model': model_name,
            'total_questions': len(common_questions),
            'direct_accuracy': direct_accuracy,
            'rag_accuracy': rag_accuracy,
            'accuracy_improvement': rag_accuracy - direct_accuracy,
            'agreement_rate': agreement / len(common_questions) if common_questions else 0,
            'rag_improvements': rag_improvements,
            'direct_improvements': direct_improvements,
            'retrieval_analysis': retrieval_analysis
        }
        
        return comparison
    
    def analyze_retrieval_quality(self, rag_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze retrieval quality metrics."""
        similarities = []
        river_found_count = 0
        num_results_list = []
        
        for result in rag_results.values():
            retrieval_info = result.get('retrieval_info', {})
            similarities.append(retrieval_info.get('top_similarity', 0.0))
            if retrieval_info.get('river_found', False):
                river_found_count += 1
            num_results_list.append(retrieval_info.get('num_results', 0))
        
        return {
            'avg_similarity': np.mean(similarities) if similarities else 0.0,
            'min_similarity': np.min(similarities) if similarities else 0.0,
            'max_similarity': np.max(similarities) if similarities else 0.0,
            'river_found_rate': river_found_count / len(rag_results) if rag_results else 0.0,
            'avg_num_results': np.mean(num_results_list) if num_results_list else 0.0
        }
    
    def generate_detailed_analysis(self, model_name: str) -> Dict[str, Any]:
        """Generate detailed analysis with per-question breakdown."""
        direct_results = self.load_direct_results(model_name)
        rag_results = self.load_rag_results(model_name)
        
        # Get common questions
        common_questions = set(direct_results['results'].keys()).intersection(set(rag_results['results'].keys()))
        
        detailed_analysis = []
        
        for qid in common_questions:
            direct_result = direct_results['results'][qid]
            rag_result = rag_results['results'][qid]
            
            analysis = {
                'question_id': qid,
                'question': direct_result['question'],
                'river_name': direct_result.get('river_name', ''),
                'direct_correct': direct_result['is_correct'],
                'rag_correct': rag_result['is_correct'],
                'agreement': direct_result['is_correct'] == rag_result['is_correct'],
                'rag_improvement': rag_result['is_correct'] and not direct_result['is_correct'],
                'retrieval_similarity': rag_result.get('retrieval_info', {}).get('top_similarity', 0.0),
                'river_found': rag_result.get('retrieval_info', {}).get('river_found', False)
            }
            
            detailed_analysis.append(analysis)
        
        return detailed_analysis
    
    def save_comparison_report(self, comparison: Dict[str, Any], detailed_analysis: List[Dict[str, Any]]):
        """Save comprehensive comparison report."""
        report = {
            'summary': comparison,
            'detailed_analysis': detailed_analysis,
            'timestamp': str(np.datetime64('now'))
        }
        
        report_path = f"{self.output_dir}/comparison_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Comparison report saved to {report_path}")
        
        # Generate summary text
        self.generate_summary_text(comparison)
    
    def generate_summary_text(self, comparison: Dict[str, Any]):
        """Generate human-readable summary."""
        summary_path = f"{self.output_dir}/comparison_summary.txt"
        
        with open(summary_path, 'w') as f:
            f.write(f"RAG vs Direct LLM Comparison Report\n")
            f.write(f"Model: {comparison['model']}\n")
            f.write(f"Generated: {comparison.get('timestamp', 'Unknown')}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Overall Performance:\n")
            f.write(f"  Total Questions: {comparison['total_questions']}\n")
            f.write(f"  Direct LLM Accuracy: {comparison['direct_accuracy']:.2%}\n")
            f.write(f"  RAG Accuracy: {comparison['rag_accuracy']:.2%}\n")
            f.write(f"  Accuracy Improvement: {comparison['accuracy_improvement']:+.2%}\n")
            f.write(f"  Agreement Rate: {comparison['agreement_rate']:.2%}\n\n")
            
            f.write(f"Improvement Analysis:\n")
            f.write(f"  Questions RAG improved: {comparison['rag_improvements']}\n")
            f.write(f"  Questions Direct LLM better: {comparison['direct_improvements']}\n\n")
            
            retrieval = comparison['retrieval_analysis']
            f.write(f"Retrieval Quality:\n")
            f.write(f"  Average Similarity: {retrieval['avg_similarity']:.3f}\n")
            f.write(f"  River Found Rate: {retrieval['river_found_rate']:.2%}\n")
            f.write(f"  Average Results per Query: {retrieval['avg_num_results']:.1f}\n")
        
        print(f"Summary text saved to {summary_path}")


def main():
    """Main comparison function."""
    config_path = 'config/rag_config.json'
    analyzer = ComparisonAnalyzer(config_path)
    
    model_name = "anthropic/claude-sonnet-4.5"
    
    # Generate comparison
    comparison = analyzer.compare_results(model_name)
    
    # Generate detailed analysis
    detailed_analysis = analyzer.generate_detailed_analysis(model_name)
    
    # Save report
    analyzer.save_comparison_report(comparison, detailed_analysis)
    
    # Print summary
    print(f"\nComparison Summary:")
    print(f"Direct LLM Accuracy: {comparison['direct_accuracy']:.2%}")
    print(f"RAG Accuracy: {comparison['rag_accuracy']:.2%}")
    print(f"Improvement: {comparison['accuracy_improvement']:+.2%}")
    print(f"Agreement Rate: {comparison['agreement_rate']:.2%}")


if __name__ == "__main__":
    main()
