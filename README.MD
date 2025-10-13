# World Mind POC-1: Ontological Repair for Hallucination

This project is a proof-of-concept demonstrating a "truth-constrained" architecture for Large Language Models (LLMs). It uses a knowledge graph as a "Licensing Oracle" to validate factual claims before they are generated, forcing the system to abstain when a claim is not supported by evidence or violates formal constraints.

Info: https://gemini.google.com/app/4cae5f51830c5945

## Quick Start

1.  **Setup Environment:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Experiment:**
    The `Makefile` provides commands to run the entire pipeline.

    ```bash
    # Run all steps: download data, build graph, validate, and test
    make all

    # Or run steps individually
    make data
    make build
    make validate
    make test
    ```