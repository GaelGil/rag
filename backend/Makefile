# Simple Makefile for backend application using uv


# Install dependencies using uv
.PHONY: install
install:
	@echo "Installing dependencies with uv..."
	uv sync

# Run the application
.PHONY: run
run:
	@echo "Starting application..."
	.venv/bin/python main.py
# IF running locally uncomment for database setup
# 	flask db upgrade
# 	.venv/bin/python seed.py
