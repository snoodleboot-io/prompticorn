# Architect Mode - Real Root Cause (NEW Kilo IDE Change)

## The Discovery

You were right - this is a **regression due to newer Kilo IDE requirements**.

### Timeline

1. **Old Kilo IDE:** Custom modes worked without needing `kilo.json`
2. **New Kilo IDE:** Requires explicit `kilo.json` config to locate and register custom modes
3. **Promptosaurus:** Builder never updated to create `kilo.json`
4. **Result:** Architect (and other custom modes) don't show in new Kilo IDE

### Evidence

**Git history shows:**
- Commit e3eb435 (Mar 7, 2026): "fix: resolve custom modes not being generated"
  - This fixed custom modes being created
  - But did NOT create `kilo.json` (wasn't required by old Kilo yet)

- Newer Kilo IDE versions: Require `kilo.json` for custom mode registration
  - Custom modes in `.kilocodemodes` now need explicit registration
  - Without `kilo.json`, IDE doesn't know where to find `.kilocodemodes`

- No commit in promptosaurus history ever creates `kilo.json`
  - Not created by builder (KiloIDEBuilder)
  - Not tracked in git
  - Disappeared when Kilo IDE updated

### The Real Fix

The **builder should generate `kilo.json`** to support newer Kilo IDE.

**Required change in `promptosaurus/builders/kilo/kilo_ide.py`:**

In `KiloIDEBuilder.build()` method, add:

```python
# 6. Generate kilo.json for newer Kilo IDE support
actions.append(self._create_kilo_json(output, dry_run))
```

And add method:

```python
def _create_kilo_json(self, output: Path, dry_run: bool) -> str:
    """Create kilo.json config for custom modes (required by newer Kilo IDE).
    
    Newer Kilo IDE versions require explicit configuration to find
    custom modes defined in .kilocodemodes.
    """
    kilo_json = {
        "$schema": "https://app.kilo.ai/config.json",
        "modes": {
            "path": ".kilocodemodes"
        }
    }
    
    if dry_run:
        return "[dry-run] kilo.json (custom modes config)"
    
    import json
    dest = output / "kilo.json"
    dest.write_text(json.dumps(kilo_json, indent=2), encoding="utf-8")
    return "✓ kilo.json"
```

## Summary

**Not an issue with architect definition** - the definition is correct.

**Not an issue with .kilocodemodes** - file is properly generated.

**The actual issue:** Newer Kilo IDE requires `kilo.json` to register custom modes, but the builder was never updated to create it.

**The fix:** Update `KiloIDEBuilder` to generate `kilo.json` alongside `.kilocodemodes`.

This is a **builder code change**, not a prompt/config change.

