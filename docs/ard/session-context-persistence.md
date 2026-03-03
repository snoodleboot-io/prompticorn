# Architecture Requirements Document: Session Context Persistence

**Document Version:** 1.0  
**Date:** 2026-03-02  
**Status:** Draft  
**Author:** AI Assistant  

---

## 1. Executive Summary

This ARD provides technical architecture and implementation guidance for the Session Context Persistence feature. The system will maintain persistent session files that capture context across mode switches, enabling continuity in the development workflow.

**Key Technical Decisions:**
- Session storage in `.prompty/session/` as Markdown files with YAML frontmatter
- Pydantic models for type-safe session data management
- Git branch association for natural workflow alignment
- Automatic session lifecycle management (no user intervention required)

---

## 2. Architecture Overview

### 2.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mode Prompts                             │
│  (architect, code, test, debug, refactor, document, etc.)      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ 1. Check for session
                     │ 2. Read/Create session
                     │ 3. Update on actions
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Session Management Module                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ SessionFile │  │SessionContext│  │   GitBranchResolver     │  │
│  │   Manager   │  │   Manager    │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File System Storage                        │
│  .prompty/session/                                              │
│    ├── session_abc123.md                                       │
│    ├── session_def456.md                                       │
│    └── .current                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `SessionFileManager` | File I/O operations, directory management, YAML parsing |
| `SessionContextManager` | Session lifecycle, context updates, mode transitions |
| `GitBranchResolver` | Branch detection, validation, main branch handling |
| `SessionModels` | Pydantic data models for type-safe session data |

### 2.3 Data Flow

1. **Mode Startup:** Mode checks for active session via pointer file
2. **Session Resolution:** If no active session, search by current branch name
3. **Session Creation:** If no session found, create new session file
4. **Context Loading:** Load session context into mode prompt
5. **Context Updates:** Mode updates session on significant actions/mode switches

---

## 3. Data Models (Pydantic)

### 3.1 Core Models

```python
# promptcli/session/models.py

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class ModeHistoryEntry(BaseModel):
    """Represents a single mode transition in session history."""
    
    mode: str = Field(..., description="Mode slug (e.g., 'architect', 'code')")
    entered_at: datetime = Field(..., description="When this mode was entered")
    exited_at: Optional[datetime] = Field(
        None, description="When this mode was exited (null if current)"
    )
    summary: str = Field(
        default="", description="Summary of work done in this mode"
    )
    
    @field_validator('mode')
    @classmethod
    def validate_mode_slug(cls, v: str) -> str:
        """Ensure mode slug is lowercase and URL-safe."""
        return v.lower().strip()


class ActionEntry(BaseModel):
    """Represents a completed action in the session."""
    
    timestamp: datetime = Field(..., description="When action was completed")
    mode: str = Field(..., description="Mode that performed the action")
    action: str = Field(..., description="Description of what was done")
    files_affected: list[str] = Field(
        default_factory=list, description="Files modified/created"
    )
    
    @field_validator('files_affected')
    @classmethod
    def validate_paths(cls, v: list[str]) -> list[str]:
        """Normalize file paths to use forward slashes."""
        return [path.replace("\\", "/") for path in v]


class SessionMetadata(BaseModel):
    """Metadata stored in YAML frontmatter of session file."""
    
    session_id: str = Field(..., description="Unique session identifier")
    branch_name: str = Field(..., description="Associated git branch")
    start_time: datetime = Field(..., description="Session creation timestamp")
    last_updated: datetime = Field(..., description="Last activity timestamp")
    current_mode: str = Field(..., description="Currently active mode")
    mode_history: list[ModeHistoryEntry] = Field(
        default_factory=list, description="Mode transition history"
    )
    context_summary: str = Field(
        default="", description="Current work context summary"
    )
    actions_taken: list[ActionEntry] = Field(
        default_factory=list, description="Log of completed actions"
    )
    version: str = Field(
        default="1.0", description="Session format version"
    )
    
    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Ensure session_id is URL-safe."""
        # Replace any problematic characters
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in v)
        return safe_id.lower()


class Session(BaseModel):
    """Complete session object including metadata and body content."""
    
    metadata: SessionMetadata
    body: str = Field(
        default="", description="Markdown body with detailed notes"
    )
    
    def to_markdown(self) -> str:
        """Serialize session to Markdown with YAML frontmatter."""
        import yaml
        
        # Convert metadata to YAML
        yaml_content = yaml.safe_dump(
            self.metadata.model_dump(mode='json'),
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )
        
        # Build full document
        parts = [
            "---",
            yaml_content.strip(),
            "---",
            "",
            self.body.strip() if self.body else "# Session Notes\n"
        ]
        
        return "\n".join(parts)
    
    @classmethod
    def from_markdown(cls, content: str) -> "Session":
        """Parse session from Markdown with YAML frontmatter."""
        import yaml
        import re
        
        # Extract frontmatter
        pattern = r'^---\s*\n(.*?)\n---\s*\n?(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if not match:
            raise ValueError("Invalid session file format: missing frontmatter")
        
        yaml_content, body = match.groups()
        
        # Parse metadata
        metadata_dict = yaml.safe_load(yaml_content)
        metadata = SessionMetadata(**metadata_dict)
        
        return cls(metadata=metadata, body=body.strip())
```

### 3.2 Session ID Generation

```python
# promptcli/session/id_generator.py

from datetime import datetime
import uuid


def generate_session_id() -> str:
    """Generate a unique, URL-safe session ID.
    
    Format: sess_{YYYYMMDD}_{random_suffix}
    Example: sess_20260302_a1b2c3d4
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = uuid.uuid4().hex[:8]
    return f"sess_{date_part}_{random_suffix}"


def generate_session_filename(session_id: str) -> str:
    """Generate filename for session file."""
    return f"session_{session_id}.md"
```

---

## 4. Session Management Module Design

### 4.1 SessionFileManager

```python
# promptcli/session/file_manager.py

import os
from pathlib import Path
from typing import Optional

from .models import Session


class SessionFileManager:
    """Manages file I/O operations for session storage."""
    
    SESSION_DIR = ".prompty/session"
    CURRENT_POINTER = ".current"
    
    def __init__(self, root_path: Optional[Path] = None):
        """Initialize with optional root path (defaults to current directory)."""
        self.root = root_path or Path.cwd()
        self.session_dir = self.root / self.SESSION_DIR
    
    def ensure_session_directory(self) -> None:
        """Create session directory if it doesn't exist."""
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def get_session_path(self, session_id: str) -> Path:
        """Get full path for a session file."""
        from .id_generator import generate_session_filename
        filename = generate_session_filename(session_id)
        return self.session_dir / filename
    
    def read_session(self, session_id: str) -> Optional[Session]:
        """Read session from file. Returns None if not found."""
        session_path = self.get_session_path(session_id)
        
        if not session_path.exists():
            return None
        
        try:
            content = session_path.read_text(encoding='utf-8')
            return Session.from_markdown(content)
        except Exception as e:
            # Log error but don't crash - session corruption shouldn't break workflow
            print(f"Warning: Failed to read session {session_id}: {e}")
            return None
    
    def write_session(self, session: Session) -> None:
        """Write session to file."""
        self.ensure_session_directory()
        
        session_path = self.get_session_path(session.metadata.session_id)
        content = session.to_markdown()
        
        # Atomic write: write to temp file, then rename
        temp_path = session_path.with_suffix('.tmp')
        temp_path.write_text(content, encoding='utf-8')
        temp_path.replace(session_path)
    
    def read_current_pointer(self) -> Optional[str]:
        """Read current session ID from pointer file."""
        pointer_path = self.session_dir / self.CURRENT_POINTER
        
        if not pointer_path.exists():
            return None
        
        try:
            return pointer_path.read_text(encoding='utf-8').strip()
        except Exception:
            return None
    
    def write_current_pointer(self, session_id: str) -> None:
        """Update current session pointer."""
        self.ensure_session_directory()
        
        pointer_path = self.session_dir / self.CURRENT_POINTER
        pointer_path.write_text(session_id, encoding='utf-8')
    
    def find_sessions_by_branch(self, branch_name: str) -> list[Session]:
        """Find all sessions associated with a branch."""
        sessions = []
        
        if not self.session_dir.exists():
            return sessions
        
        for file_path in self.session_dir.glob("session_*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                session = Session.from_markdown(content)
                
                if session.metadata.branch_name == branch_name:
                    sessions.append(session)
            except Exception:
                # Skip corrupted session files
                continue
        
        # Sort by last_updated descending
        sessions.sort(
            key=lambda s: s.metadata.last_updated,
            reverse=True
        )
        
        return sessions
    
    def list_all_sessions(self) -> list[Session]:
        """List all sessions sorted by last activity."""
        sessions = []
        
        if not self.session_dir.exists():
            return sessions
        
        for file_path in self.session_dir.glob("session_*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                session = Session.from_markdown(content)
                sessions.append(session)
            except Exception:
                continue
        
        sessions.sort(
            key=lambda s: s.metadata.last_updated,
            reverse=True
        )
        
        return sessions
```

### 4.2 GitBranchResolver

```python
# promptcli/session/git_resolver.py

import subprocess
from pathlib import Path
from typing import Optional


class GitBranchResolver:
    """Resolves git branch information for session association."""
    
    MAIN_BRANCHES = {'main', 'master', 'trunk'}
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
    
    def _run_git_command(self, args: list[str]) -> Optional[str]:
        """Run git command and return output, or None on failure."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def get_current_branch(self) -> Optional[str]:
        """Get current git branch name."""
        # Try modern git command first
        branch = self._run_git_command(['branch', '--show-current'])
        
        if branch:
            return branch
        
        # Fallback: parse from rev-parse
        ref = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        
        if ref and ref != 'HEAD':
            return ref
        
        return None
    
    def is_main_branch(self, branch_name: Optional[str] = None) -> bool:
        """Check if current/main branch is a main/trunk branch."""
        if branch_name is None:
            branch_name = self.get_current_branch()
        
        if not branch_name:
            return False
        
        return branch_name.lower() in self.MAIN_BRANCHES
    
    def is_detached_head(self) -> bool:
        """Check if in detached HEAD state."""
        ref = self._run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        return ref == 'HEAD'
    
    def suggest_branch_name(self) -> str:
        """Suggest a feature branch name based on context."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"feature/session_{timestamp}"
```

### 4.3 SessionContextManager

```python
# promptcli/session/context_manager.py

from datetime import datetime
from typing import Optional

from .models import Session, SessionMetadata, ModeHistoryEntry, ActionEntry
from .file_manager import SessionFileManager
from .git_resolver import GitBranchResolver
from .id_generator import generate_session_id


class SessionContextManager:
    """High-level interface for session lifecycle management."""
    
    def __init__(
        self,
        file_manager: Optional[SessionFileManager] = None,
        git_resolver: Optional[GitBranchResolver] = None
    ):
        self.file_manager = file_manager or SessionFileManager()
        self.git_resolver = git_resolver or GitBranchResolver()
        self._current_session: Optional[Session] = None
    
    def get_or_create_session(
        self,
        mode: str,
        context_summary: str = ""
    ) -> Session:
        """Get existing session or create new one for current branch."""
        
        # Check for active session via pointer
        current_id = self.file_manager.read_current_pointer()
        
        if current_id:
            session = self.file_manager.read_session(current_id)
            if session:
                # Update mode history if mode changed
                if session.metadata.current_mode != mode:
                    self._record_mode_transition(session, mode)
                
                session.metadata.current_mode = mode
                session.metadata.last_updated = datetime.utcnow()
                
                if context_summary:
                    session.metadata.context_summary = context_summary
                
                self.file_manager.write_session(session)
                self._current_session = session
                return session
        
        # No active session - search by branch
        branch = self.git_resolver.get_current_branch()
        
        if branch:
            sessions = self.file_manager.find_sessions_by_branch(branch)
            if sessions:
                # Use most recent session for this branch
                session = sessions[0]
                self._record_mode_transition(session, mode)
                session.metadata.current_mode = mode
                session.metadata.last_updated = datetime.utcnow()
                
                if context_summary:
                    session.metadata.context_summary = context_summary
                
                self.file_manager.write_session(session)
                self.file_manager.write_current_pointer(session.metadata.session_id)
                self._current_session = session
                return session
        
        # Create new session
        return self._create_new_session(mode, branch, context_summary)
    
    def _create_new_session(
        self,
        mode: str,
        branch: Optional[str],
        context_summary: str
    ) -> Session:
        """Create a new session."""
        
        now = datetime.utcnow()
        session_id = generate_session_id()
        
        metadata = SessionMetadata(
            session_id=session_id,
            branch_name=branch or "unknown",
            start_time=now,
            last_updated=now,
            current_mode=mode,
            mode_history=[
                ModeHistoryEntry(
                    mode=mode,
                    entered_at=now,
                    summary="Session started"
                )
            ],
            context_summary=context_summary or f"New session on {branch or 'unknown branch'}"
        )
        
        session = Session(metadata=metadata)
        
        self.file_manager.write_session(session)
        self.file_manager.write_current_pointer(session_id)
        self._current_session = session
        
        return session
    
    def _record_mode_transition(self, session: Session, new_mode: str) -> None:
        """Record mode transition in session history."""
        now = datetime.utcnow()
        
        # Mark current mode as exited
        if session.metadata.mode_history:
            current_entry = session.metadata.mode_history[-1]
            if current_entry.mode == session.metadata.current_mode:
                current_entry.exited_at = now
        
        # Add new mode entry
        session.metadata.mode_history.append(
            ModeHistoryEntry(
                mode=new_mode,
                entered_at=now,
                summary=""
            )
        )
    
    def record_action(
        self,
        action: str,
        files_affected: Optional[list[str]] = None
    ) -> None:
        """Record a completed action in the current session."""
        if not self._current_session:
            return
        
        action_entry = ActionEntry(
            timestamp=datetime.utcnow(),
            mode=self._current_session.metadata.current_mode,
            action=action,
            files_affected=files_affected or []
        )
        
        self._current_session.metadata.actions_taken.append(action_entry)
        self._current_session.metadata.last_updated = datetime.utcnow()
        
        self.file_manager.write_session(self._current_session)
    
    def update_context_summary(self, summary: str) -> None:
        """Update the context summary for current session."""
        if not self._current_session:
            return
        
        self._current_session.metadata.context_summary = summary
        self._current_session.metadata.last_updated = datetime.utcnow()
        
        self.file_manager.write_session(self._current_session)
    
    def update_mode_summary(self, summary: str) -> None:
        """Update summary for current mode in history."""
        if not self._current_session or not self._current_session.metadata.mode_history:
            return
        
        current_entry = self._current_session.metadata.mode_history[-1]
        current_entry.summary = summary
        
        self.file_manager.write_session(self._current_session)
    
    def get_session_summary(self) -> str:
        """Get human-readable summary of current session."""
        if not self._current_session:
            return "No active session"
        
        meta = self._current_session.metadata
        
        lines = [
            f"Session: {meta.session_id}",
            f"Branch: {meta.branch_name}",
            f"Current Mode: {meta.current_mode}",
            f"Started: {meta.start_time.isoformat()}",
            f"Last Updated: {meta.last_updated.isoformat()}",
            f"Mode History: {len(meta.mode_history)} transitions",
            f"Actions: {len(meta.actions_taken)} recorded",
            "",
            "Context:",
            meta.context_summary
        ]
        
        return "\n".join(lines)
```

---

## 5. File Format Specification

### 5.1 Session File Structure

```markdown
---
session_id: "sess_20260302_a1b2c3d4"
branch_name: "feature/session-persistence"
start_time: "2026-03-02T15:30:00Z"
last_updated: "2026-03-02T16:45:22Z"
current_mode: "architect"
mode_history:
  - mode: "architect"
    entered_at: "2026-03-02T15:30:00Z"
    exited_at: "2026-03-02T16:15:00Z"
    summary: "Designed session persistence architecture"
  - mode: "code"
    entered_at: "2026-03-02T16:15:00Z"
    exited_at: "2026-03-02T16:45:22Z"
    summary: "Implemented session manager module"
  - mode: "architect"
    entered_at: "2026-03-02T16:45:22Z"
    summary: "Reviewing implementation approach"
context_summary: |
  Designing session context persistence for PromptCLI.
  Key decisions: store in .prompty/session/, YAML frontmatter,
  branch-based association, automatic lifecycle management.
actions_taken:
  - timestamp: "2026-03-02T15:35:00Z"
    mode: "architect"
    action: "Created PRD for session persistence"
    files_affected:
      - "docs/prd/session-context-persistence.md"
  - timestamp: "2026-03-02T16:00:00Z"
    mode: "architect"
    action: "Created ARD with data models"
    files_affected:
      - "docs/ard/session-context-persistence.md"
version: "1.0"
---

# Session: Session Context Persistence Design

## Current Focus
Creating comprehensive design documents for session context persistence feature.

## Key Decisions
1. Store session files in `.prompty/session/` directory
2. Use YAML frontmatter for metadata, Markdown body for details
3. Branch association allows multiple sessions per branch
4. Automatic session lifecycle (create/update without user action)

## Open Questions
- Should we implement session archival/rotation for large files?
- How to handle merge conflicts in session context?

## Notes
- Consider encryption for sensitive context
- Future: session sharing between team members
```

### 5.2 YAML Schema Details

| Field | Type | Constraints | Example |
|-------|------|-------------|---------|
| `session_id` | string | URL-safe, unique | `sess_20260302_a1b2c3d4` |
| `branch_name` | string | Required | `feature/session-persistence` |
| `start_time` | datetime | ISO 8601 UTC | `2026-03-02T15:30:00Z` |
| `last_updated` | datetime | ISO 8601 UTC | `2026-03-02T16:45:22Z` |
| `current_mode` | string | Valid mode slug | `architect` |
| `mode_history` | array | Ordered chronologically | See ModeHistoryEntry |
| `context_summary` | string | Multi-line allowed | Free text |
| `actions_taken` | array | Chronological order | See ActionEntry |
| `version` | string | Semantic versioning | `1.0` |

### 5.3 Versioning Strategy

Session format versions follow semantic versioning:
- **Major:** Breaking changes to schema (requires migration)
- **Minor:** Additive changes (new optional fields)
- **Patch:** Documentation/fixes (no schema change)

Migration path for v1.0 → v2.0:
1. Detect version mismatch on read
2. Apply transformation rules
3. Update version field
4. Write back in new format

---

## 6. Mode Prompt Update Requirements

### 6.1 Session Awareness Section

All mode prompts must include a "Session Context Awareness" section. Here's the template:

```markdown
## Session Context Awareness

Before beginning work, check for session context:

1. **Check Active Session:**
   - Read `.prompty/session/.current` for active session ID
   - If no pointer exists, search for sessions by current branch name
   - If multiple sessions exist for branch, use most recently active

2. **Session Initialization:**
   - If no session found, create new session with:
     - `session_id`: Generate using `sess_YYYYMMDD_random` format
     - `branch_name`: Current git branch (or "unknown")
     - `current_mode`: Your mode slug
     - `start_time`: Current UTC timestamp
     - `context_summary`: Brief description of user's initial request

3. **Context Reading:**
   - Read session metadata (YAML frontmatter)
   - Review mode_history for previous work
   - Check actions_taken for completed work
   - Read body section for detailed notes

4. **During Operation:**
   - Maintain awareness of session context
   - Reference previous decisions and work
   - Update context_summary when focus changes

5. **On Mode Switch:**
   - Update mode_history:
     - Set `exited_at` for current mode entry
     - Add new entry for next mode with `entered_at`
   - Update `current_mode` field
   - Provide summary of work done in current mode

6. **On Action Completion:**
   - Log significant actions to `actions_taken`:
     - `timestamp`: Current UTC time
     - `mode`: Current mode slug
     - `action`: Description of what was done
     - `files_affected`: List of modified/created files
   - Update `last_updated` timestamp

7. **File Updates:**
   - Write session file after significant changes
   - Use atomic write (temp file + rename) for safety
   - Update `.current` pointer when session changes
```

### 6.2 Mode-Specific Additions

**Architect Mode:**
```markdown
### Architect Session Additions

When in architect mode, additionally capture:
- Design decisions and their rationale
- Task breakdowns and acceptance criteria
- Architecture diagrams or data models (as text descriptions)
- Identified risks and constraints

Update `context_summary` with:
- Current design focus
- Key decisions made
- Open questions or blockers
```

**Code Mode:**
```markdown
### Code Session Additions

When in code mode, additionally capture:
- Implementation progress
- Technical decisions and tradeoffs
- Code patterns established
- Files being worked on

Update `context_summary` with:
- Current implementation task
- Files modified in this session
- Technical approach being followed
```

**Test Mode:**
```markdown
### Test Session Additions

When in test mode, additionally capture:
- Test coverage goals
- Test scenarios being implemented
- Test results and failures

Update `context_summary` with:
- Testing focus area
- Coverage metrics
- Failing tests requiring attention
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# tests/session/test_models.py

import pytest
from datetime import datetime
from promptcli.session.models import (
    ModeHistoryEntry, ActionEntry, SessionMetadata, Session
)


class TestModeHistoryEntry:
    def test_valid_creation(self):
        entry = ModeHistoryEntry(
            mode="architect",
            entered_at=datetime.utcnow(),
            summary="Design work"
        )
        assert entry.mode == "architect"
    
    def test_mode_slug_normalization(self):
        entry = ModeHistoryEntry(
            mode="ARCHITECT",
            entered_at=datetime.utcnow()
        )
        assert entry.mode == "architect"


class TestSession:
    def test_roundtrip_serialization(self):
        session = Session(
            metadata=SessionMetadata(
                session_id="sess_test_001",
                branch_name="feature/test",
                start_time=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                current_mode="code"
            ),
            body="# Test Session\nNotes here"
        )
        
        markdown = session.to_markdown()
        restored = Session.from_markdown(markdown)
        
        assert restored.metadata.session_id == session.metadata.session_id
        assert restored.body == session.body
    
    def test_invalid_markdown_raises(self):
        with pytest.raises(ValueError, match="missing frontmatter"):
            Session.from_markdown("No frontmatter here")
```

### 7.2 Integration Tests

```python
# tests/session/test_integration.py

import pytest
from pathlib import Path
from promptcli.session.file_manager import SessionFileManager
from promptcli.session.context_manager import SessionContextManager
from promptcli.session.models import Session, SessionMetadata


class TestSessionFileManager:
    def test_session_lifecycle(self, tmp_path):
        manager = SessionFileManager(root_path=tmp_path)
        
        # Create session
        session = Session(
            metadata=SessionMetadata(
                session_id="test_001",
                branch_name="feature/test",
                start_time=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                current_mode="architect"
            )
        )
        
        # Write
        manager.write_session(session)
        
        # Read back
        loaded = manager.read_session("test_001")
        assert loaded is not None
        assert loaded.metadata.branch_name == "feature/test"
        
        # Pointer
        manager.write_current_pointer("test_001")
        assert manager.read_current_pointer() == "test_001"


class TestSessionContextManager:
    def test_get_or_create_creates_new(self, tmp_path):
        file_mgr = SessionFileManager(root_path=tmp_path)
        ctx_mgr = SessionContextManager(file_manager=file_mgr)
        
        session = ctx_mgr.get_or_create_session("architect")
        
        assert session.metadata.session_id.startswith("sess_")
        assert session.metadata.current_mode == "architect"
    
    def test_mode_transition_recorded(self, tmp_path):
        file_mgr = SessionFileManager(root_path=tmp_path)
        ctx_mgr = SessionContextManager(file_manager=file_mgr)
        
        # Start in architect
        session = ctx_mgr.get_or_create_session("architect")
        initial_history_len = len(session.metadata.mode_history)
        
        # Switch to code
        session = ctx_mgr.get_or_create_session("code")
        
        assert len(session.metadata.mode_history) == initial_history_len + 1
        assert session.metadata.current_mode == "code"
```

### 7.3 Test Coverage Requirements

| Component | Coverage Target |
|-----------|-----------------|
| `models.py` | 95%+ |
| `file_manager.py` | 90%+ |
| `context_manager.py` | 90%+ |
| `git_resolver.py` | 85%+ |
| `id_generator.py` | 100% |

### 7.4 Edge Cases to Test

1. **Corrupted Session Files:** Graceful handling of invalid YAML
2. **Detached HEAD State:** Session creation without branch name
3. **Concurrent Access:** File locking/atomic writes
4. **Large Sessions:** Performance with many actions/history entries
5. **Special Characters:** Branch names with special characters
6. **Missing Git:** Behavior when not in a git repository

---

## 8. Error Handling & Recovery

### 8.1 Error Categories

| Category | Examples | Handling |
|----------|----------|----------|
| File I/O | Permission denied, disk full | Log warning, continue without session |
| Parse Errors | Invalid YAML, missing fields | Log error, treat as new session |
| Git Errors | Not a repo, command failed | Use "unknown" branch, continue |
| Concurrency | File locked by another process | Retry with backoff, then skip |

### 8.2 Recovery Strategies

```python
# Error recovery example
try:
    session = Session.from_markdown(content)
except yaml.YAMLError as e:
    logger.warning(f"Corrupted session file: {e}")
    # Attempt to extract what we can
    session = attempt_session_recovery(content)
except ValidationError as e:
    logger.warning(f"Invalid session data: {e}")
    # Create new session, preserve what we can
    session = create_session_from_partial(content)
```

---

## 9. Performance Considerations

### 9.1 Benchmarks

| Operation | Target | Notes |
|-----------|--------|-------|
| Session read | < 10ms | Includes YAML parsing |
| Session write | < 20ms | Includes atomic rename |
| Branch resolution | < 100ms | Git command timeout |
| List all sessions | < 50ms | For < 100 sessions |

### 9.2 Optimization Strategies

1. **Lazy Loading:** Don't parse body content unless needed
2. **Caching:** Cache current session in memory
3. **Indexing:** Consider index file for large session counts
4. **Async I/O:** Use async file operations if available

---

## 10. Security Considerations

### 10.1 Data Sensitivity

Session files may contain:
- File paths (potentially sensitive)
- Code snippets in context
- Business logic descriptions

**Mitigations:**
- Session files in `.gitignore` by default
- Optional encryption for sensitive contexts
- No secrets or credentials in session data

### 10.2 File Permissions

```python
# Set restrictive permissions on session files
import os
session_path.chmod(0o600)  # Owner read/write only
```

---

## 11. Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Pydantic models (`models.py`)
- [ ] File manager (`file_manager.py`)
- [ ] ID generator (`id_generator.py`)
- [ ] Git resolver (`git_resolver.py`)

### Phase 2: Session Management
- [ ] Context manager (`context_manager.py`)
- [ ] Session lifecycle integration
- [ ] Mode prompt updates

### Phase 3: Integration & Polish
- [ ] CLI commands for session management
- [ ] Session archival/rotation
- [ ] Comprehensive testing
- [ ] Documentation

---

## 12. Dependencies

### Required
- `pydantic >= 2.0` - Data validation
- `pyyaml >= 6.0` - YAML parsing
- `python >= 3.10` - Type hints, match statements

### Optional
- `cryptography` - Session file encryption
- `pytest-asyncio` - Async testing
