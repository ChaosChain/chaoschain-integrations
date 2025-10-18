.PHONY: help venv install install-dev install-all clean fmt lint typecheck test test-unit test-integration test-contract test-cov build publish proto-gen sidecar-build health-check

# Python interpreter
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest

# Virtual environment
VENV_DIR ?= venv
VENV_ACTIVATE = . $(VENV_DIR)/bin/activate

help:
	@echo "ChaosChain Integrations - Development Commands"
	@echo "==============================================="
	@echo "Setup:"
	@echo "  make venv          - Create virtual environment"
	@echo "  make install       - Install base dependencies"
	@echo "  make install-dev   - Install with dev dependencies"
	@echo "  make install-all   - Install with all adapter extras"
	@echo ""
	@echo "Development:"
	@echo "  make fmt           - Format code (black, isort, ruff)"
	@echo "  make lint          - Lint code (ruff)"
	@echo "  make typecheck     - Type check (mypy)"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-contract - Run contract tests only"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo ""
	@echo "Build & Release:"
	@echo "  make build         - Build distribution packages"
	@echo "  make publish       - Publish to PyPI (requires credentials)"
	@echo "  make clean         - Clean build artifacts"
	@echo ""
	@echo "Sidecars:"
	@echo "  make proto-gen     - Generate protobuf code"
	@echo "  make sidecar-build - Build all sidecar binaries"
	@echo "  make health-check  - Check health of running sidecars"

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created. Activate with: source $(VENV_DIR)/bin/activate"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"
	pre-commit install

install-all:
	$(PIP) install -e ".[all,dev]"
	pre-commit install

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*_pb2.py" -delete
	find . -type f -name "*_pb2.pyi" -delete
	find . -type f -name "*_pb2_grpc.py" -delete

fmt:
	@echo "Running black..."
	$(PYTHON) -m black chaoschain_integrations/ scripts/
	@echo "Running isort..."
	$(PYTHON) -m isort chaoschain_integrations/ scripts/
	@echo "Running ruff fix..."
	$(PYTHON) -m ruff check --fix chaoschain_integrations/ scripts/

lint:
	@echo "Running ruff..."
	$(PYTHON) -m ruff check chaoschain_integrations/ scripts/
	@echo "Running black check..."
	$(PYTHON) -m black --check chaoschain_integrations/ scripts/
	@echo "Running isort check..."
	$(PYTHON) -m isort --check chaoschain_integrations/ scripts/

typecheck:
	@echo "Running mypy..."
	$(PYTHON) -m mypy chaoschain_integrations/

test:
	$(PYTEST) -v

test-unit:
	$(PYTEST) -v -m unit

test-integration:
	$(PYTEST) -v -m integration

test-contract:
	$(PYTEST) -v -m contract

test-cov:
	$(PYTEST) -v --cov --cov-report=html --cov-report=term

build: clean
	$(PYTHON) -m build

publish: build
	$(PYTHON) -m twine upload dist/*

proto-gen:
	@echo "Generating protobuf code for ZeroG..."
	cd sidecars/zerog/proto && python -m grpc_tools.protoc -I. --python_out=../../../chaoschain_integrations/storage/zerog/ --grpc_python_out=../../../chaoschain_integrations/storage/zerog/ --pyi_out=../../../chaoschain_integrations/storage/zerog/ zerog_storage.proto
	cd sidecars/zerog/proto && python -m grpc_tools.protoc -I. --python_out=../../../chaoschain_integrations/compute/zerog/ --grpc_python_out=../../../chaoschain_integrations/compute/zerog/ --pyi_out=../../../chaoschain_integrations/compute/zerog/ zerog_compute.proto
	@echo "Generating protobuf code for Eigen..."
	cd sidecars/eigen/proto && python -m grpc_tools.protoc -I. --python_out=../../../chaoschain_integrations/compute/eigen/ --grpc_python_out=../../../chaoschain_integrations/compute/eigen/ --pyi_out=../../../chaoschain_integrations/compute/eigen/ eigen_compute.proto
	@echo "Done!"

sidecar-build:
	@echo "Building ZeroG sidecar..."
	cd sidecars/zerog/go && make build
	@echo "Building Eigen sidecar..."
	cd sidecars/eigen/go && make build
	@echo "Building CRE sidecar..."
	cd sidecars/chainlink_cre/go && make build
	@echo "All sidecars built!"

health-check:
	@echo "Checking sidecar health..."
	$(PYTHON) scripts/health_check.py

