#!/bin/bash

source ../../ci/base.sh

# Mypy
# pipx run can't be used because mypy needs the pydantic plugin to be installed in the same venv (using pipx inject)
run pipx install `spec mypy`
run pipx inject mypy `spec pydantic`
run $PIPX_BIN_DIR/mypy src --python-executable=$(which python)

# Pylint
run pylint --rcfile=../../.pylintrc src tests

# Dlint
unset PYTHONDEVMODE  # Suppress DeprecationWarnings given by flake8/dlint in dev mode
run pipx run --spec `spec dlint` flake8 --select=DUO src
export PYTHONDEVMODE=1

# pip-audit
unset PYTHONDEVMODE  # Suppress ResourceWarnings given by pip-audit in dev mode
run pipx run `spec pip-audit` --strict --progress-spinner=off -r requirements/requirements-dev.txt
export PYTHONDEVMODE=1

# Safety
run pipx run `spec safety` check --bare -r requirements/requirements-dev.txt

# Bandit
run pipx run `spec bandit` --quiet --recursive src/

# Vulture
run pipx run `spec vulture` --min-confidence 0 src/ tests/ .vulture_ignore_list.py

# Black
run pipx run `spec black` --check src tests
