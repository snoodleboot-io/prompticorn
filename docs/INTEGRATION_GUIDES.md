# Integration Guides

How to integrate Prompticorn with your development workflow and CI/CD pipelines.

## Table of Contents

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [IDE Integration](#ide-integration)
- [Docker Integration](#docker-integration)

---

## GitHub Actions

### Automated Configuration Validation

```yaml
# .github/workflows/prompticorn-validate.yml

name: Validate Prompticorn Configuration

on:
  push:
    branches: [main, develop]
    paths:
      - '.prompticorn.yaml'
      - 'prompticorn/**'
  pull_request:
    branches: [main, develop]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install prompticorn
        run: pip install prompticorn
      
      - name: Validate configuration
        run: prompticorn validate
      
      - name: List registered agents
        run: prompticorn list
```

### Auto-Update Agent Configs on Config Change

```yaml
# .github/workflows/prompticorn-regenerate.yml

name: Regenerate Agent Configurations

on:
  push:
    branches: [main]
    paths:
      - '.prompticorn.yaml'

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install prompticorn
        run: pip install prompticorn
      
      - name: Regenerate all tool configs
        run: |
          prompticorn switch kilo-ide
          prompticorn switch cline
          prompticorn switch cursor
          prompticorn switch copilot
      
      - name: Commit if changed
        run: |
          git config user.name "Bot"
          git config user.email "bot@example.com"
          git add .kilo .clinerules .cursor .github/copilot-instructions.md
          git commit -m "chore: regenerate agent configurations" || echo "No changes"
          git push
```

### Persona-Based Testing

```yaml
# .github/workflows/test-personas.yml

name: Test with Different Personas

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        personas:
          - software_engineer
          - qa_tester
          - devops_engineer
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install prompticorn
        run: pip install prompticorn
      
      - name: Test with persona - ${{ matrix.personas }}
        run: |
          # Create a test config with this persona
          cat > test-config.yaml << EOF
          version: "1.0"
          repository:
            type: "single-language"
          spec:
            language: "python"
            runtime: "3.12"
            package_manager: "uv"
            testing_framework: "pytest"
          variant: "minimal"
          active_personas: ["${{ matrix.personas }}"]
          EOF
          
          # Copy to actual config
          cp test-config.yaml .prompticorn.yaml
          
          # Validate and regenerate
          prompticorn validate
          prompticorn list
```

---

## GitLab CI

### Validate on Every Push

```yaml
# .gitlab-ci.yml

stages:
  - validate
  - build

validate-config:
  stage: validate
  image: python:3.12
  script:
    - pip install prompticorn
    - prompticorn validate
    - prompticorn list
  only:
    changes:
      - .prompticorn.yaml
      - prompticorn/**

regenerate-configs:
  stage: build
  image: python:3.12
  script:
    - pip install prompticorn
    - prompticorn switch kilo-ide
    - prompticorn switch cline
    - prompticorn switch cursor
  artifacts:
    paths:
      - .kilo/
      - .clinerules
      - .cursor/
      - .github/
  only:
    - main
```

---

## Pre-Commit Hooks

### Validate Before Commit

```yaml
# .pre-commit-config.yaml

repos:
  - repo: local
    hooks:
      - id: prompticorn-validate
        name: Validate Prompticorn Config
        entry: prompticorn validate
        language: system
        files: ^\.prompticorn\.yaml$
        pass_filenames: false
        always_run: false
        stages: [commit]
      
      - id: prompticorn-list
        name: List Prompticorn Agents
        entry: bash -c 'prompticorn list'
        language: system
        files: ^(\.prompticorn\.yaml|prompticorn/.*)$
        pass_filenames: false
        always_run: false
        stages: [manual]  # Run with: pre-commit run -a
```

### Installation

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks
pre-commit install

# Run manually (optional)
pre-commit run -a
```

---

## IDE Integration

### VS Code

#### Settings (`.vscode/settings.json`)

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "[markdown]": {
    "editor.defaultFormatter": "prettier/prettier",
    "editor.formatOnSave": true
  }
}
```

#### Tasks (`.vscode/tasks.json`)

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate Prompticorn",
      "type": "shell",
      "command": "prompticorn",
      "args": ["validate"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "List Prompticorn Agents",
      "type": "shell",
      "command": "prompticorn",
      "args": ["list"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Initialize Prompticorn",
      "type": "shell",
      "command": "prompticorn",
      "args": ["init"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

#### Usage

- Press `Ctrl+Shift+B` to run tasks
- Select "Validate Prompticorn" or other tasks

### JetBrains IDEs (IntelliJ, PyCharm, WebStorm)

#### External Tool Configuration

1. **Settings** → **Tools** → **External Tools**
2. **+ Add new tool** → Configure:

```
Name:       Prompticorn Validate
Program:    prompticorn
Arguments:  validate
Working directory: $ProjectFileDir$
```

3. Repeat for:
   - `prompticorn list`
   - `prompticorn init`

#### Usage

- **Tools** → **Prompticorn Validate**
- Or create keyboard shortcuts in Keymap settings

---

## Docker Integration

### Dockerfile

```dockerfile
# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install prompticorn
RUN pip install --no-cache-dir prompticorn

# Copy configuration
COPY .prompticorn.yaml .

# Validate on build
RUN prompticorn validate

# Copy agents
COPY prompticorn/ ./prompticorn/

CMD ["prompticorn", "list"]
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  prompticorn:
    build: .
    volumes:
      - .:/app
    command: prompticorn validate
```

### Usage

```bash
# Build and validate
docker-compose build

# Run validation
docker-compose run prompticorn prompticorn validate

# Run other commands
docker-compose run prompticorn prompticorn list
```

---

## Makefile Integration

```makefile
# Makefile

.PHONY: init list validate switch update clean

# Initialize
init:
	prompticorn init

# List agents
list:
	prompticorn list

# Validate config
validate:
	prompticorn validate

# Switch tool
switch:
	prompticorn switch

# Update configuration
update:
	prompticorn update

# Clean generated files
clean:
	rm -rf .kilo .clinerules .cursor .github/copilot-instructions.md

# Validate and regenerate
rebuild: clean validate init

# Run all
all: validate init list
```

### Usage

```bash
make init         # Run interactive init
make validate     # Validate configuration
make list         # List agents
make rebuild      # Clean and rebuild everything
```

---

## Environment Variables

### Using Environment Variables in Config

```bash
# Set environment variables
export PROMPTICORN_LANGUAGE=python
export PROMPTICORN_RUNTIME=3.12
export PROMPTICORN_PACKAGE_MANAGER=uv

# Use in scripts
prompticorn validate

# Unset when done
unset PROMPTICORN_LANGUAGE
unset PROMPTICORN_RUNTIME
unset PROMPTICORN_PACKAGE_MANAGER
```

### CI/CD Secrets

```yaml
# GitHub Actions example
- name: Setup Prompticorn Config
  env:
    LANGUAGE: ${{ secrets.LANGUAGE }}
    RUNTIME: ${{ secrets.RUNTIME }}
  run: |
    prompticorn validate
```

---

## Continuous Integration Best Practices

1. **Always Validate Before Deploy**
   ```bash
   prompticorn validate || exit 1
   ```

2. **Version Your Configuration**
   ```bash
   # Add version to config
   version: "1.0"
   ```

3. **Test Multiple Personas**
   - Matrix testing with different personas
   - Ensures all role-based configs work

4. **Regenerate on Configuration Change**
   - Auto-commit regenerated files
   - Keep configs in sync with .prompticorn.yaml

5. **Monitor Configuration Files**
   - Alert on .prompticorn.yaml changes
   - Validate before merge

---

## Reference

- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Setup guide
- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Configuration reference
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

