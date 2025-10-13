"""
WorldMind Core Library

A framework for building truth-constrained LLM architectures
using knowledge graphs as licensing oracles.
"""

__version__ = "0.1.0"

from worldmind.graph_store import GraphStore
from worldmind.models.auditor import ConsistencyAuditor
from worldmind.models.policy import AbstentionPolicy

__all__ = ["GraphStore", "ConsistencyAuditor", "AbstentionPolicy"]

