.PHONY: help poc1 poc2 clean-all

# Default target shows available commands
help:
	@echo "WorldMind Project - Available Commands:"
	@echo ""
	@echo "  make poc1           - Run POC1 (Philosophers experiment)"
	@echo "  make poc2           - Run POC2 (Military Battles experiment)"
	@echo "  make clean-all      - Clean all experiment artifacts"
	@echo ""
	@echo "To work with a specific experiment, cd into its directory:"
	@echo "  cd experiments/poc1_philosophers && make all"
	@echo "  cd experiments/poc2_battles && make all"

# Quick access to POC1
poc1:
	cd experiments/poc1_philosophers && $(MAKE) all

# Quick access to POC2
poc2:
	cd experiments/poc2_battles && $(MAKE) all

# Clean all experiments
clean-all:
	cd experiments/poc1_philosophers && $(MAKE) clean
	cd experiments/poc2_battles && $(MAKE) clean
