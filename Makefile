# Chrome Extension Downloader Makefile

.PHONY: help install install-dev test test-cov lint format clean build dist upload docs

# Default target
help:
	@echo "Chrome Extension Downloader - Available Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run test suite"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black"
	@echo "  clean        Clean build artifacts"
	@echo ""
	@echo "Packaging:"
	@echo "  build        Build package"
	@echo "  dist         Create distribution packages"
	@echo "  upload       Upload to PyPI (requires credentials)"
	@echo ""
	@echo "Documentation:"
	@echo "  docs         Generate documentation"
	@echo ""
	@echo "Examples:"
	@echo "  example-single    Download single extension"
	@echo "  example-batch     Download multiple extensions"
	@echo "  example-interactive Run interactive mode"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

# Testing
test:
	python -m pytest test_chrome_extension_downloader.py -v

test-cov:
	python -m pytest test_chrome_extension_downloader.py --cov=chrome_extension_downloader --cov-report=html --cov-report=term

# Code Quality
lint:
	flake8 chrome_extension_downloader.py crx_utils.py test_chrome_extension_downloader.py
	mypy chrome_extension_downloader.py crx_utils.py

format:
	black chrome_extension_downloader.py crx_utils.py test_chrome_extension_downloader.py

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf downloads/
	rm -rf cache/
	rm -f chrome_extension_downloader.log
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Packaging
build:
	python setup.py build

dist:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/*

# Documentation
docs:
	@echo "Documentation is available in:"
	@echo "  - README.md (main documentation)"
	@echo "  - API_DOCUMENTATION.md (detailed API reference)"
	@echo "  - Inline code documentation"

# Examples
example-single:
	python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --verbose

example-batch:
	python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome --verbose

example-interactive:
	python chrome_extension_downloader.py --interactive

example-config:
	python chrome_extension_downloader.py --create-config

example-from-file:
	python chrome_extension_downloader.py --from-file sample_extensions.txt --verbose

# Development workflow
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

dev-test: format lint test
	@echo "All development checks passed!"

# Quick development cycle
quick-test:
	python -m pytest test_chrome_extension_downloader.py::TestConfig::test_default_config -v

# Docker support (if needed)
docker-build:
	docker build -t chrome-extension-downloader .

docker-run:
	docker run -it --rm chrome-extension-downloader

# Version management
version:
	@python -c "import setup; print(setup.version)"

# Check dependencies
check-deps:
	pip check

# Security check
security-check:
	pip install safety
	safety check

# Full CI pipeline
ci: clean install-dev format lint test test-cov security-check
	@echo "CI pipeline completed successfully!"
