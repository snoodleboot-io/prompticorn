# Integration Guides

How to integrate Promptosaurus with your development workflow and CI/CD pipelines.

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
# .github/workflows/promptosaurus-validate.yml

name: Validate Promptosaurus Configuration

on:
  push:
    branches: [main, develop]
    paths:
      - '.promptosaurus.yaml'
      - 'promptosaurus/**'
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
      
      - name: Install promptosaurus
        run: pip install promptosaurus
      
      - name: Validate configuration
        run: promptosaurus validate
      
      - name: List registered agents
        run: promptosaurus list
```

### Auto-Update Agent Configs on Config Change

```yaml
# .github/workflows/promptosaurus-regenerate.yml

name: Regenerate Agent Configurations

on:
  push:
    branches: [main]
    paths:
      - '.promptosaurus.yaml'

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
      
      - name: Install promptosaurus
        run: pip install promptosaurus
      
      - name: Regenerate all tool configs
        run: |
          promptosaurus switch kilo-ide
          promptosaurus switch cline
          promptosaurus switch cursor
          promptosaurus switch copilot
      
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
      
      - name: Install promptosaurus
        run: pip install promptosaurus
      
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
          cp test-config.yaml .promptosaurus.yaml
          
          # Validate and regenerate
          promptosaurus validate
          promptosaurus list
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
    - pip install promptosaurus
    - promptosaurus validate
    - promptosaurus list
  only:
    changes:
      - .promptosaurus.yaml
      - promptosaurus/**

regenerate-configs:
  stage: build
  image: python:3.12
  script:
    - pip install promptosaurus
    - promptosaurus switch kilo-ide
    - promptosaurus switch cline
    - promptosaurus switch cursor
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
      - id: promptosaurus-validate
        name: Validate Promptosaurus Config
        entry: promptosaurus validate
        language: system
        files: ^\.promptosaurus\.yaml$
        pass_filenames: false
        always_run: false
        stages: [commit]
      
      - id: promptosaurus-list
        name: List Promptosaurus Agents
        entry: bash -c 'promptosaurus list'
        language: system
        files: ^(\.promptosaurus\.yaml|promptosaurus/.*)$
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
      "label": "Validate Promptosaurus",
      "type": "shell",
      "command": "promptosaurus",
      "args": ["validate"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "List Promptosaurus Agents",
      "type": "shell",
      "command": "promptosaurus",
      "args": ["list"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Initialize Promptosaurus",
      "type": "shell",
      "command": "promptosaurus",
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
- Select "Validate Promptosaurus" or other tasks

### JetBrains IDEs (IntelliJ, PyCharm, WebStorm)

#### External Tool Configuration

1. **Settings** → **Tools** → **External Tools**
2. **+ Add new tool** → Configure:

```
Name:       Promptosaurus Validate
Program:    promptosaurus
Arguments:  validate
Working directory: $ProjectFileDir$
```

3. Repeat for:
   - `promptosaurus list`
   - `promptosaurus init`

#### Usage

- **Tools** → **Promptosaurus Validate**
- Or create keyboard shortcuts in Keymap settings

---

## Docker Integration

### Dockerfile

```dockerfile
# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install promptosaurus
RUN pip install --no-cache-dir promptosaurus

# Copy configuration
COPY .promptosaurus.yaml .

# Validate on build
RUN promptosaurus validate

# Copy agents
COPY promptosaurus/ ./promptosaurus/

CMD ["promptosaurus", "list"]
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  promptosaurus:
    build: .
    volumes:
      - .:/app
    command: promptosaurus validate
```

### Usage

```bash
# Build and validate
docker-compose build

# Run validation
docker-compose run promptosaurus promptosaurus validate

# Run other commands
docker-compose run promptosaurus promptosaurus list
```

---

## Makefile Integration

```makefile
# Makefile

.PHONY: init list validate switch update clean

# Initialize
init:
	promptosaurus init

# List agents
list:
	promptosaurus list

# Validate config
validate:
	promptosaurus validate

# Switch tool
switch:
	promptosaurus switch

# Update configuration
update:
	promptosaurus update

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
export PROMPTOSAURUS_LANGUAGE=python
export PROMPTOSAURUS_RUNTIME=3.12
export PROMPTOSAURUS_PACKAGE_MANAGER=uv

# Use in scripts
promptosaurus validate

# Unset when done
unset PROMPTOSAURUS_LANGUAGE
unset PROMPTOSAURUS_RUNTIME
unset PROMPTOSAURUS_PACKAGE_MANAGER
```

### CI/CD Secrets

```yaml
# GitHub Actions example
- name: Setup Promptosaurus Config
  env:
    LANGUAGE: ${{ secrets.LANGUAGE }}
    RUNTIME: ${{ secrets.RUNTIME }}
  run: |
    promptosaurus validate
```

---

## Continuous Integration Best Practices

1. **Always Validate Before Deploy**
   ```bash
   promptosaurus validate || exit 1
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
   - Keep configs in sync with .promptosaurus.yaml

5. **Monitor Configuration Files**
   - Alert on .promptosaurus.yaml changes
   - Validate before merge

---

## Reference

- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Setup guide
- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Configuration reference
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

