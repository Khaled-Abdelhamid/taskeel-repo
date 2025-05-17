.PHONY: help server ui clean clean-pkg all

# Default target
help:
	@echo "Available commands:"
	@echo "  make server         - Run the FastAPI server"
	@echo "  make ui             - Run the ui frontend"
	@echo "  make all            - Run both server and ui"
	@echo "  make clean          - Run all clean commands"
	@echo "  make clean-pkg      - Clean Python package build artifacts"
	@echo "  make clean-pyc      - Remove Python file artifacts"
	@echo "  make clean-test     - Remove test artifacts"

# Server commands
server:
	@echo "Starting FastAPI server..."
	./start_api.sh
ui:
	@echo "Starting ui frontend..."
	./start_web_ui.sh

clean-pkg:
	@echo "Cleaning Python package build artifacts..."
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -path "*.egg-info*" -exec rm -rf {} +
	find . -name "*.egg" -exec rm -f {} +
	find . -name "*.eggs" -exec rm -rf {} +
	find . -name ".eggs" -exec rm -rf {} +
	find . -name "dist" -exec rm -rf {} +
	find . -name "build" -exec rm -rf {} +
	find . -name "*.dist-info" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	rm -rf *.egg-info
	rm -rf .eggs

# Update the clean command to include the new clean-pkg command
clean: clean-pkg
	@echo "Removing Python artifacts..."
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	@echo "Removing test artifacts..."
	find . -name '.pytest_cache' -exec rm -fr {} +
	find . -name '.coverage' -exec rm -f {} +
	find . -name 'htmlcov' -exec rm -fr {} +
	find . -name '.tox' -exec rm -fr {} +

# Run both server and UI
all:
	@echo "Starting both server and UI..."
	./start_api.sh & 
	sleep 5
	./.start_web_ui.sh
