"""Single source of the package version.

The real version is injected by CI/CD at build time
(see .github/scripts/calculate_version.py and .github/workflows/ci-cd.yml).
Local and editable installs use this dev placeholder.
"""

__version__ = "0.0.0.dev0"
