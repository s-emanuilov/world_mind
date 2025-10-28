#!/usr/bin/env python3
"""
Generate all publication-quality figures for the Rivers experimental paper.
Saves figures to the figures/ subdirectory.
"""

import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Change to figures directory
output_dir = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(output_dir, exist_ok=True)

# Set publication-quality style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'

# Global figure settings for consistency
FIGURE_WIDTH = 10
FIGURE_HEIGHT = 6
DPI = 300
FONT_SIZE = 11
TITLE_SIZE = 13
LABEL_SIZE = 11

# Color scheme
COLOR_BASELINE = '#E74C3C'  # Red - poor performance
COLOR_FINETUNE = '#F39C12'  # Orange - marginal improvement
COLOR_RAG = '#3498DB'       # Blue - strong performance  
COLOR_GRAPH_RAG = '#2ECC71' # Green - architectural innovation
COLOR_ABSTAIN = '#95A5A6'   # Gray - abstention/uncertainty

plt.rcParams.update({
    'font.size': FONT_SIZE,
    'axes.titlesize': TITLE_SIZE,
    'axes.labelsize': LABEL_SIZE,
    'xtick.labelsize': FONT_SIZE - 1,
    'ytick.labelsize': FONT_SIZE - 1,
    'legend.fontsize': FONT_SIZE - 1,
    'figure.titlesize': TITLE_SIZE + 2,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
})

def save_figure(fig, filename):
    """Save figure in both PNG and PDF formats."""
    png_path = os.path.join(output_dir, f'{filename}.png')
    pdf_path = os.path.join(output_dir, f'{filename}.pdf')
    fig.savefig(png_path, dpi=DPI, bbox_inches='tight')
    fig.savefig(pdf_path, bbox_inches='tight')
    print(f"✓ Saved: {filename}.png and {filename}.pdf")

def generate_figure_1():
    """Figure 1: Baseline LLM Performance on River Q&A Dataset"""
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=DPI)
    
    # Data
    models = ['Gemma 3-4B\nInstruct', 'Claude Sonnet\n4.5', 'Gemini 2.5\nFlash Lite']
    accuracy = [16.7, 42.0, 50.1]
    questions = [7839, 4208, 12174]
    
    # Create bars
    bars = ax.bar(models, accuracy, color=COLOR_BASELINE, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    
    # Add question count annotations
    for i, (bar, q_count) in enumerate(zip(bars, questions)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'n={q_count:,}',
                ha='center', va='bottom', fontsize=FONT_SIZE-2, style='italic')
        # Add percentage on bar
        ax.text(bar.get_x() + bar.get_width()/2., height/2,
                f'{accuracy[i]:.1f}%',
                ha='center', va='center', fontsize=FONT_SIZE+1, 
                fontweight='bold', color='white')
    
    # Add random chance reference line
    ax.axhline(y=20, color='gray', linestyle='--', linewidth=2, 
               label='Random chance (20%)', alpha=0.7)
    
    # Styling
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_xlabel('Model', fontweight='bold')
    ax.set_title('Baseline LLM Performance Without Grounding\nMultiple-Choice Question Answering on River Dataset',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 65)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Add subtle background for better readability
    ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    save_figure(fig, 'figure_1_baseline_performance')
    plt.close(fig)

def generate_figure_2():
    """Figure 2: Fine-Tuning Results - Statistical Learning Limitations"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIGURE_WIDTH*1.5, FIGURE_HEIGHT), dpi=DPI)
    
    # Left panel: Accuracy comparison
    models = ['Gemma 3-4B\nBaseline', 'Gemma-Factual\n(Fine-tuned)', 'Gemma-Abstain\n(Fine-tuned)']
    accuracy = [16.7, 8.5, 8.6]
    colors = [COLOR_BASELINE, COLOR_FINETUNE, COLOR_FINETUNE]
    
    bars1 = ax1.bar(models, accuracy, color=colors, alpha=0.8, 
                    edgecolor='black', linewidth=1.5)
    
    # Add accuracy labels on bars
    for bar, acc in zip(bars1, accuracy):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=FONT_SIZE, fontweight='bold')
    
    ax1.set_ylabel('Accuracy (%)', fontweight='bold')
    ax1.set_xlabel('Model Variant', fontweight='bold')
    ax1.set_title('Fine-Tuning Failed to Improve Accuracy',
                  fontweight='bold', pad=15)
    ax1.set_ylim(0, 25)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_facecolor('#FAFAFA')
    
    # Add annotation showing performance degradation
    ax1.annotate('', xy=(1, 8.5), xytext=(0, 16.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=2, alpha=0.7))
    ax1.text(0.5, 13, 'Performance\ndegradation', ha='center', 
            fontsize=FONT_SIZE-2, color='red', style='italic')
    
    # Right panel: Abstention breakdown for Gemma-Abstain
    categories = ['Correct\nAnswers', 'Incorrect\nAnswers', 'Appropriate\nAbstentions', 
                  'Inappropriate\nAbstentions']
    counts = [1527, 5831, 9318, 7110]
    total = sum(counts)
    percentages = [c/total*100 for c in counts]
    
    colors2 = [COLOR_GRAPH_RAG, COLOR_BASELINE, COLOR_ABSTAIN, COLOR_FINETUNE]
    bars2 = ax2.bar(categories, percentages, color=colors2, alpha=0.8,
                    edgecolor='black', linewidth=1.5)
    
    # Add percentage labels
    for bar, pct, count in zip(bars2, percentages, counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{pct:.1f}%\n(n={count:,})',
                ha='center', va='bottom', fontsize=FONT_SIZE-2)
    
    ax2.set_ylabel('Percentage of Total Responses (%)', fontweight='bold')
    ax2.set_xlabel('Response Category', fontweight='bold')
    ax2.set_title('Abstention Behavior: Non-Deterministic\nAbstention Precision: 56.7%',
                  fontweight='bold', pad=15)
    ax2.set_ylim(0, 60)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_facecolor('#FAFAFA')
    
    # Add annotation for poor precision
    ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)
    ax2.text(3.5, 51, 'Near-random\nabstention', ha='right', 
            fontsize=FONT_SIZE-2, color='gray', style='italic')
    
    plt.tight_layout()
    save_figure(fig, 'figure_2_finetuning_results')
    plt.close(fig)

def generate_figure_3():
    """Figure 3: RAG vs Graph-RAG - Equivalent Accuracy, Different Architectures"""
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=DPI)
    
    # Data
    systems = ['Embedding-based\nRAG', 'Graph-based\nRAG with\nLicensing Oracle']
    accuracy = [89.5, 89.1]
    questions = [23781, 16626]
    colors = [COLOR_RAG, COLOR_GRAPH_RAG]
    
    # Create bars with custom styling
    x_pos = np.arange(len(systems))
    bars = ax.bar(x_pos, accuracy, color=colors, alpha=0.85,
                  edgecolor='black', linewidth=2, width=0.6)
    
    # Add accuracy labels
    for i, (bar, acc, q) in enumerate(zip(bars, accuracy, questions)):
        height = bar.get_height()
        # Percentage
        ax.text(bar.get_x() + bar.get_width()/2., height - 5,
                f'{acc:.1f}%',
                ha='center', va='top', fontsize=FONT_SIZE+3, 
                fontweight='bold', color='white')
        # Question count
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'n={q:,} questions',
                ha='center', va='bottom', fontsize=FONT_SIZE-1, style='italic')
    
    # Add capability annotations
    rag_capabilities = ['✗ No validation', '✗ No abstention', '✗ No provenance']
    graph_capabilities = ['✓ SHACL validation', '✓ Deterministic abstention', '✓ Triple provenance']
    
    y_start = 75
    for i, cap in enumerate(rag_capabilities):
        ax.text(-0.35, y_start - i*6, cap, ha='left', va='top',
               fontsize=FONT_SIZE-1, color='#E74C3C', family='monospace')
    
    for i, cap in enumerate(graph_capabilities):
        ax.text(0.65, y_start - i*6, cap, ha='left', va='top',
               fontsize=FONT_SIZE-1, color='#2ECC71', family='monospace')
    
    # Styling
    ax.set_xticks(x_pos)
    ax.set_xticklabels(systems)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('RAG System Comparison: Equivalent Accuracy, Different Architectures\n' + 
                 'Statistical Retrieval vs. Structural Enforcement',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#FAFAFA')
    
    # Add subtle difference annotation
    ax.plot([0, 1], [89.5, 89.1], 'k--', alpha=0.3, linewidth=1)
    ax.text(0.5, 89.3, 'Δ = 0.4pp\n(statistically equivalent)', 
           ha='center', va='bottom', fontsize=FONT_SIZE-2, 
           style='italic', color='gray',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    save_figure(fig, 'figure_3_rag_comparison')
    plt.close(fig)

def generate_figure_4():
    """Figure 4: Complete Experimental Progression"""
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH*1.3, FIGURE_HEIGHT*1.1), dpi=DPI)
    
    # Data for all approaches
    approaches = [
        'Gemma-3-4B\nBaseline',
        'Gemma\nFactual\nFT',
        'Gemma\nAbstain\nFT', 
        'Gemini\nBaseline',
        'RAG\nEmbedding',
        'Graph-RAG\nOracle'
    ]
    
    accuracies = [16.7, 8.5, 8.6, 50.1, 89.5, 89.1]
    
    # Color coding by approach type
    colors_by_type = [
        COLOR_BASELINE,    # Baseline
        COLOR_FINETUNE,    # Fine-tune factual
        COLOR_FINETUNE,    # Fine-tune abstain
        COLOR_BASELINE,    # Gemini baseline
        COLOR_RAG,         # RAG
        COLOR_GRAPH_RAG    # Graph-RAG
    ]
    
    # Create bar chart
    x_pos = np.arange(len(approaches))
    bars = ax.bar(x_pos, accuracies, color=colors_by_type, alpha=0.85,
                  edgecolor='black', linewidth=1.5)
    
    # Add accuracy labels on bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=FONT_SIZE-1, fontweight='bold')
    
    # Add approach category separators and labels
    ax.axvline(x=2.5, color='black', linestyle='--', linewidth=2, alpha=0.3)
    ax.axvline(x=4.5, color='black', linestyle='--', linewidth=2, alpha=0.3)
    
    # Category labels
    ax.text(1, 95, 'Statistical Learning', ha='center', fontsize=FONT_SIZE, 
           fontweight='bold', color='#E74C3C',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                    edgecolor='#E74C3C', linewidth=2))
    
    ax.text(3.5, 95, 'Baseline\n(No Grounding)', ha='center', fontsize=FONT_SIZE, 
           fontweight='bold', color='#E74C3C',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                    edgecolor='#E74C3C', linewidth=2))
    
    ax.text(5, 95, 'Architectural Enforcement', ha='center', fontsize=FONT_SIZE, 
           fontweight='bold', color='#2ECC71',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                    edgecolor='#2ECC71', linewidth=2))
    
    # Add improvement arrows
    # Statistical learning plateau
    ax.annotate('', xy=(2, 8.6), xytext=(0, 16.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=2.5, alpha=0.6))
    ax.text(1, 13, 'Degradation', ha='center', fontsize=FONT_SIZE-2, 
           color='red', style='italic', weight='bold')
    
    # Jump to RAG
    ax.annotate('', xy=(4, 89.5), xytext=(3, 50.1),
                arrowprops=dict(arrowstyle='->', color='green', lw=2.5, alpha=0.6))
    ax.text(3.5, 70, '+39.4pp\nContext\nProvision', ha='center', fontsize=FONT_SIZE-2, 
           color='green', style='italic', weight='bold')
    
    # Styling
    ax.set_xticks(x_pos)
    ax.set_xticklabels(approaches, fontsize=FONT_SIZE-1)
    ax.set_ylabel('Accuracy (%)', fontweight='bold')
    ax.set_title('Experimental Progression: From Statistical Learning to Architectural Enforcement\n' +
                 'Comprehensive Comparison of Five Approaches to Factual Grounding',
                 fontweight='bold', pad=20)
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_facecolor('#FAFAFA')
    
    # Add legend for approach types
    legend_elements = [
        mpatches.Patch(facecolor=COLOR_BASELINE, edgecolor='black', 
                      label='Baseline (No Grounding)'),
        mpatches.Patch(facecolor=COLOR_FINETUNE, edgecolor='black', 
                      label='Fine-Tuning (Statistical)'),
        mpatches.Patch(facecolor=COLOR_RAG, edgecolor='black', 
                      label='RAG (Embedding-based)'),
        mpatches.Patch(facecolor=COLOR_GRAPH_RAG, edgecolor='black', 
                      label='Graph-RAG (Licensing Oracle)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.95)
    
    plt.tight_layout()
    save_figure(fig, 'figure_4_complete_progression')
    plt.close(fig)

def generate_figure_5():
    """Figure 5: Architectural Capabilities Comparison Matrix"""
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH*1.2, FIGURE_HEIGHT*1.3), dpi=DPI)
    
    # Define approaches and capabilities
    approaches = [
        'Baseline LLM',
        'Fine-Tuning\n(Factual)',
        'Fine-Tuning\n(Abstention)',
        'RAG\n(Embedding)',
        'Graph-RAG\n(Oracle)'
    ]
    
    capabilities = [
        'High Factual\nAccuracy\n(>80%)',
        'Deterministic\nAbstention',
        'Formal\nValidation',
        'Interpretable\nProvenance',
        'Domain\nTransfer',
        'Zero\nRetraining'
    ]
    
    # Capability matrix (1 = has capability, 0.5 = partial, 0 = lacks)
    capability_matrix = np.array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],  # Baseline
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # Fine-tune factual
        [0.0, 0.3, 0.0, 0.0, 0.0, 0.0],  # Fine-tune abstain (poor abstention)
        [1.0, 0.0, 0.0, 0.3, 0.0, 0.0],  # RAG (high accuracy, weak provenance)
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],  # Graph-RAG (all capabilities)
    ])
    
    # Create heatmap
    im = ax.imshow(capability_matrix, cmap='RdYlGn', aspect='auto', 
                   vmin=0, vmax=1, alpha=0.8)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(capabilities)))
    ax.set_yticks(np.arange(len(approaches)))
    ax.set_xticklabels(capabilities, fontsize=FONT_SIZE-1)
    ax.set_yticklabels(approaches, fontsize=FONT_SIZE)
    
    # Rotate x labels for readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    
    # Add text annotations
    for i in range(len(approaches)):
        for j in range(len(capabilities)):
            value = capability_matrix[i, j]
            if value == 1.0:
                text = '✓'
                color = 'darkgreen'
                size = FONT_SIZE + 8
            elif value >= 0.3:
                text = '◐'
                color = 'orange'
                size = FONT_SIZE + 4
            else:
                text = '✗'
                color = 'darkred'
                size = FONT_SIZE + 4
            
            ax.text(j, i, text, ha='center', va='center',
                   color=color, fontsize=size, fontweight='bold')
    
    # Add accuracy annotations on the right
    accuracies_for_matrix = [50.1, 8.5, 8.6, 89.5, 89.1]
    for i, acc in enumerate(accuracies_for_matrix):
        ax.text(len(capabilities) + 0.3, i, f'{acc:.1f}%',
               ha='left', va='center', fontsize=FONT_SIZE-1,
               fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', 
                        facecolor='white', 
                        edgecolor='black',
                        linewidth=1))
    
    ax.text(len(capabilities) + 0.3, -0.7, 'Accuracy',
           ha='left', va='center', fontsize=FONT_SIZE-1,
           fontweight='bold', style='italic')
    
    # Styling
    ax.set_title('Architectural Capabilities Comparison Matrix\n' +
                 'Graph-RAG Provides Unique Combination of High Accuracy and Formal Guarantees',
                 fontweight='bold', pad=20, fontsize=TITLE_SIZE)
    
    # Add colorbar legend
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', 
                       pad=0.15, aspect=40, shrink=0.8)
    cbar.set_label('Capability Score', fontweight='bold')
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(['Absent', 'Partial', 'Full'])
    
    # Add grid for readability
    ax.set_xticks(np.arange(len(capabilities))-0.5, minor=True)
    ax.set_yticks(np.arange(len(approaches))-0.5, minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=1.5)
    
    # Highlight the Graph-RAG row
    rect = Rectangle((-0.5, 3.5), len(capabilities), 1, 
                     linewidth=3, edgecolor='#2ECC71', 
                     facecolor='none', linestyle='-')
    ax.add_patch(rect)
    
    plt.tight_layout()
    save_figure(fig, 'figure_5_capabilities_matrix')
    plt.close(fig)

def main():
    """Generate all five figures for the experimental paper."""
    print("=" * 60)
    print("Generating all experimental figures...")
    print("=" * 60)
    print()
    
    print("[1/5] Generating baseline performance comparison...")
    generate_figure_1()
    print()
    
    print("[2/5] Generating fine-tuning results...")
    generate_figure_2()
    print()
    
    print("[3/5] Generating RAG comparison...")
    generate_figure_3()
    print()
    
    print("[4/5] Generating complete experimental progression...")
    generate_figure_4()
    print()
    
    print("[5/5] Generating capabilities matrix...")
    generate_figure_5()
    print()
    
    print("=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)
    print()
    print(f"Output directory: {output_dir}")
    print()
    print("Files created:")
    print("  • figure_1_baseline_performance.png / .pdf")
    print("  • figure_2_finetuning_results.png / .pdf")
    print("  • figure_3_rag_comparison.png / .pdf")
    print("  • figure_4_complete_progression.png / .pdf")
    print("  • figure_5_capabilities_matrix.png / .pdf")
    print()
    print("All figures are publication-ready at 300 DPI.")

if __name__ == "__main__":
    main()

