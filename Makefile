.PHONY: help poc1 clean-all

# Default target shows available commands
help:
	@echo "WorldMind Project - Available Commands:"
	@echo ""
	@echo "  make poc1           - Run POC1 (Philosophers experiment)"
	@echo "  make clean-all      - Clean all experiment artifacts"
	@echo ""
	@echo "To work with a specific experiment, cd into its directory:"
	@echo "  cd experiments/poc1_philosophers && make all"

# Quick access to POC1
poc1:
	cd experiments/poc1_philosophers && $(MAKE) all

# Clean all experiments
clean-all:
	cd experiments/poc1_philosophers && $(MAKE) clean
