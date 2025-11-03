#!/usr/bin/env python3
"""
Generate 4 figures - Figure 2 with SIMPLE dashed lines (no arrows)
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

output_dir = os.path.join(os.path.dirname(__file__), 'figures')
os.makedirs(output_dir, exist_ok=True)

plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'

DPI = 300
FONT_SMALL = 10
FONT_NORMAL = 12
FONT_LARGE = 14
FONT_TITLE = 16

COLOR_BASELINE = '#D32F2F'
COLOR_FINETUNE = '#F57C00'
COLOR_RAG = '#1976D2'
COLOR_GRAPH_RAG = '#388E3C'
COLOR_ACCENT = '#00838F'

plt.rcParams.update({
    'font.size': FONT_NORMAL,
    'axes.titlesize': FONT_TITLE,
    'axes.labelsize': FONT_LARGE,
    'xtick.labelsize': FONT_NORMAL,
    'ytick.labelsize': FONT_NORMAL,
    'legend.fontsize': FONT_NORMAL,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans'],
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.facecolor': '#FAFAFA',
})

def save_figure(fig, filename):
    png_path = os.path.join(output_dir, f'{filename}.png')
    pdf_path = os.path.join(output_dir, f'{filename}.pdf')
    fig.savefig(png_path, dpi=DPI, bbox_inches='tight', facecolor='white', pad_inches=0.4)
    fig.savefig(pdf_path, bbox_inches='tight', facecolor='white', pad_inches=0.4)
    print(f"✓ {filename}")

def generate_figure_1():
    """Figure 1: RAG Comparison"""
    fig, ax = plt.subplots(figsize=(10, 7), dpi=DPI)
    
    systems = ['Embedding-based\nRAG', 'Graph-based RAG\nwith Licensing Oracle']
    accuracy = [89.5, 89.1]
    colors = [COLOR_RAG, COLOR_GRAPH_RAG]
    
    x_pos = np.arange(len(systems))
    bars = ax.bar(x_pos, accuracy, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=2.5, width=0.5)
    
    for i, (bar, acc) in enumerate(zip(bars, accuracy)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=FONT_LARGE+4, 
                fontweight='bold', color='black')
    
    ax.text(0.5, -25, 
            'RAG: No validation, No abstention, No provenance\n' +
            'Graph-RAG: SHACL validation, Deterministic abstention, Full provenance',
            ha='center', va='top', fontsize=FONT_SMALL+1,
            bbox=dict(boxstyle='round,pad=1', facecolor='white', 
                     edgecolor='black', linewidth=1.5))
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(systems, fontsize=FONT_NORMAL+2)
    ax.set_ylabel('Accuracy (%)', fontweight='bold', fontsize=FONT_LARGE+2)
    ax.set_title('RAG Comparison: Equivalent Accuracy, Different Architectures',
                 fontweight='bold', pad=20, fontsize=FONT_TITLE+2)
    ax.set_ylim(0, 105)
    
    ax.plot([0, 1], [89.5, 89.1], 'k--', alpha=0.4, linewidth=2, zorder=0)
    ax.text(0.5, 91, 'Δ = 0.4pp (equivalent)', 
           ha='center', fontsize=FONT_NORMAL, style='italic', 
           bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', 
                    alpha=0.3, edgecolor='gray', linewidth=1.5))
    
    plt.tight_layout(pad=2.5)
    save_figure(fig, 'figure_1_rag_comparison')
    plt.close(fig)

def generate_figure_2():
    """Figure 2: Progression - SIMPLE dashed lines, NO ARROWS"""
    fig, ax = plt.subplots(figsize=(16, 8), dpi=DPI)
    
    approaches = [
        'Gemma-3-4B\nBaseline',
        'Gemma\nFactual FT',
        'Gemma\nAbstain FT', 
        'Gemini 2.5\nBaseline',
        'RAG\nEmbedding',
        'Graph-RAG\nOracle'
    ]
    
    accuracies = [16.7, 8.5, 8.6, 50.1, 89.5, 89.1]
    
    colors = [
        COLOR_BASELINE,
        COLOR_FINETUNE,
        COLOR_FINETUNE,
        COLOR_BASELINE,
        COLOR_RAG,
        COLOR_GRAPH_RAG
    ]
    
    x_pos = np.arange(len(approaches))
    bars = ax.bar(x_pos, accuracies, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=2.5, width=0.7)
    
    # Labels ABOVE bars
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 4,
                f'{acc:.1f}%',
                ha='center', va='bottom', fontsize=FONT_LARGE+2, 
                fontweight='bold', color='black')
    
    # Category separators
    ax.axvline(x=2.5, color='black', linestyle='--', linewidth=3, alpha=0.5)
    ax.axvline(x=3.5, color='black', linestyle='--', linewidth=3, alpha=0.5)
    
    # Category labels
    ax.text(1, 115, 'Statistical Learning', ha='center', 
           fontsize=FONT_LARGE+2, fontweight='bold', 
           bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                    edgecolor=COLOR_FINETUNE, linewidth=3))
    
    ax.text(3, 115, 'No Grounding', ha='center', 
           fontsize=FONT_LARGE+2, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                    edgecolor=COLOR_BASELINE, linewidth=3))
    
    ax.text(5, 115, 'Architectural\nEnforcement', ha='center', 
           fontsize=FONT_LARGE+2, fontweight='bold',
           bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                    edgecolor=COLOR_GRAPH_RAG, linewidth=3))
    
    # SIMPLE annotations with dashed lines connecting points
    # Degradation: dashed line from bar 0 to bar 2
    ax.plot([0, 1, 2], [16.7, 12, 8.6], 'r--', linewidth=3, alpha=0.7, zorder=0)
    ax.text(1, 35, '−8pp\nDegradation', ha='center',
           fontsize=FONT_LARGE+1, color='red', weight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='white', 
                    edgecolor='red', linewidth=2.5, alpha=0.95))
    
    # Improvement: dashed line from bar 3 to bar 4
    ax.plot([3, 3.5, 4], [50.1, 70, 89.5], 'g--', linewidth=3, alpha=0.7, zorder=0)
    ax.text(3.5, 72, '+39pp\nImprovement', ha='center',
           fontsize=FONT_LARGE+1, color='green', weight='bold',
           bbox=dict(boxstyle='round,pad=0.7', facecolor='white', 
                    edgecolor='green', linewidth=2.5, alpha=0.95))
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(approaches, fontsize=FONT_NORMAL+1)
    ax.set_ylabel('Accuracy (%)', fontweight='bold', fontsize=FONT_LARGE+2)
    ax.set_title('Experimental Progression: Statistical Learning to Architectural Enforcement',
                 fontweight='bold', pad=25, fontsize=FONT_TITLE+2)
    ax.set_ylim(0, 130)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=COLOR_BASELINE, edgecolor='black', 
                      linewidth=2, label='Baseline'),
        mpatches.Patch(facecolor=COLOR_FINETUNE, edgecolor='black', 
                      linewidth=2, label='Fine-Tuning'),
        mpatches.Patch(facecolor=COLOR_RAG, edgecolor='black', 
                      linewidth=2, label='RAG'),
        mpatches.Patch(facecolor=COLOR_GRAPH_RAG, edgecolor='black', 
                      linewidth=2, label='Graph-RAG')
    ]
    ax.legend(handles=legend_elements, loc='upper left', 
             fontsize=FONT_NORMAL+1, framealpha=0.95, edgecolor='black')
    
    plt.tight_layout(pad=2.5)
    save_figure(fig, 'figure_2_progression')
    plt.close(fig)

def generate_figure_3():
    """Figure 3: Capabilities"""
    fig, ax = plt.subplots(figsize=(13, 8), dpi=DPI)
    
    approaches = [
        'Baseline LLM',
        'Fine-Tuning (Factual)',
        'Fine-Tuning (Abstention)',
        'RAG (Embedding)',
        'Graph-RAG (Oracle)'
    ]
    
    capabilities = [
        'High\nAccuracy',
        'Deterministic\nAbstention',
        'Formal\nValidation',
        'Provenance',
        'Domain\nTransfer',
        'Zero\nRetraining'
    ]
    
    capability_matrix = np.array([
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.5, 0.0, 0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.5, 0.0, 0.0],
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    ])
    
    from matplotlib.colors import LinearSegmentedColormap
    colors_map = ['#EF5350', '#FFF59D', '#66BB6A']
    cmap = LinearSegmentedColormap.from_list('cap', colors_map, N=100)
    
    im = ax.imshow(capability_matrix, cmap=cmap, aspect='auto', 
                   vmin=0, vmax=1, alpha=0.9)
    
    ax.set_xticks(np.arange(len(capabilities)))
    ax.set_yticks(np.arange(len(approaches)))
    ax.set_xticklabels(capabilities, fontsize=FONT_NORMAL+1)
    ax.set_yticklabels(approaches, fontsize=FONT_NORMAL+2)
    
    plt.setp(ax.get_xticklabels(), rotation=20, ha='right')
    
    for i in range(len(approaches)):
        for j in range(len(capabilities)):
            value = capability_matrix[i, j]
            if value == 1.0:
                text = 'YES'
                color = '#1B5E20'
                size = FONT_LARGE
                weight = 'bold'
            elif value >= 0.5:
                text = 'PARTIAL'
                color = '#EF6C00'
                size = FONT_NORMAL
                weight = 'bold'
            else:
                text = 'NO'
                color = '#B71C1C'
                size = FONT_NORMAL
                weight = 'normal'
            
            ax.text(j, i, text, ha='center', va='center',
                   color=color, fontsize=size, fontweight=weight)
    
    accuracies = [50.1, 8.5, 8.6, 89.5, 89.1]
    for i, acc in enumerate(accuracies):
        color = 'green' if acc > 80 else ('red' if acc < 20 else 'orange')
        ax.text(len(capabilities) + 0.6, i, f'{acc:.1f}%',
               ha='left', va='center', fontsize=FONT_NORMAL+2,
               fontweight='bold', color='black',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                        edgecolor=color, linewidth=2.5))
    
    ax.text(len(capabilities) + 0.6, -1, 'Accuracy',
           ha='left', va='center', fontsize=FONT_NORMAL+2,
           fontweight='bold', style='italic')
    
    ax.set_title('Architectural Capabilities Comparison',
                 fontweight='bold', pad=20, fontsize=FONT_TITLE+2)
    
    cbar = plt.colorbar(im, ax=ax, orientation='horizontal', 
                       pad=0.15, aspect=35, shrink=0.7)
    cbar.set_label('Capability Level', fontweight='bold', fontsize=FONT_NORMAL+1)
    cbar.set_ticks([0, 0.5, 1.0])
    cbar.set_ticklabels(['NO', 'PARTIAL', 'YES'], fontsize=FONT_NORMAL)
    
    ax.set_xticks(np.arange(len(capabilities))-0.5, minor=True)
    ax.set_yticks(np.arange(len(approaches))-0.5, minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=3)
    ax.tick_params(which='minor', size=0)
    
    rect = Rectangle((-0.5, 3.5), len(capabilities), 1, 
                     linewidth=5, edgecolor='#388E3C', 
                     facecolor='none', linestyle='-')
    ax.add_patch(rect)
    
    plt.tight_layout(pad=2.5)
    save_figure(fig, 'figure_3_capabilities')
    plt.close(fig)

def generate_figure_4():
    """Figure 4: Epistemic Discipline"""
    fig, ax = plt.subplots(figsize=(11, 8), dpi=DPI)
    
    systems = ['Fine-Tuning\n(Abstention)', 'RAG\n(Embedding)', 'Graph-RAG\n(Oracle)']
    abstention_precision = [56.7, 0, 100.0]
    false_answer_rate = [24.7, 10.5, 0.0]
    
    x = np.arange(len(systems))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, abstention_precision, width, 
                   label='Abstention Precision (%)', 
                   color=COLOR_GRAPH_RAG, alpha=0.8,
                   edgecolor='black', linewidth=2.5)
    
    bars2 = ax.bar(x + width/2, false_answer_rate, width,
                   label='False Answer Rate (%)',
                   color=COLOR_BASELINE, alpha=0.8,
                   edgecolor='black', linewidth=2.5)
    
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=FONT_LARGE+1, 
                   fontweight='bold', color='black')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., 8,
                   'N/A',
                   ha='center', va='bottom', fontsize=FONT_NORMAL, 
                   style='italic', color='gray')
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
               f'{height:.1f}%',
               ha='center', va='bottom', fontsize=FONT_LARGE+1, 
               fontweight='bold', color='black')
    
    ax.axhline(y=50, color='gray', linestyle='--', linewidth=2.5, 
              alpha=0.6, label='Random chance (50%)')
    
    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=FONT_NORMAL+2)
    ax.set_ylabel('Percentage (%)', fontweight='bold', fontsize=FONT_LARGE+2)
    ax.set_title('Epistemic Discipline: Abstention Precision vs False Answers\n' +
                 'Only Graph-RAG Achieves Perfect Precision with Zero False Answers',
                 fontweight='bold', pad=20, fontsize=FONT_TITLE+1)
    ax.set_ylim(0, 140)
    
    ax.legend(fontsize=FONT_NORMAL, loc='upper center', framealpha=0.95, 
             edgecolor='black', ncol=3, bbox_to_anchor=(0.5, 1.02))
    
    ax.text(1, -30, 
            'Higher Abstention Precision = Better (knows when to say "I don\'t know")\n' +
            'Lower False Answer Rate = Better (fewer hallucinations)',
            ha='center', fontsize=FONT_NORMAL,
            bbox=dict(boxstyle='round,pad=1', facecolor='lightyellow', 
                     edgecolor='black', linewidth=1.5))
    
    plt.tight_layout(pad=2.5)
    save_figure(fig, 'figure_4_epistemic_discipline')
    plt.close(fig)

def main():
    print("=" * 70)
    print("Generating 4 Figures - Figure 2 with DASHED LINES")
    print("=" * 70)
    print()
    
    figures = [
        ("RAG Comparison", generate_figure_1),
        ("Experimental Progression (DASHED LINES)", generate_figure_2),
        ("Capabilities Matrix", generate_figure_3),
        ("Epistemic Discipline", generate_figure_4),
    ]
    
    for i, (name, gen_func) in enumerate(figures, 1):
        print(f"[{i}/4] {name}...")
        gen_func()
    
    print()
    print("=" * 70)
    print("✓ Done!")
    print("=" * 70)
    print("Fig 2: NO ARROWS - simple dashed lines with text labels")
    print()

if __name__ == "__main__":
    main()
