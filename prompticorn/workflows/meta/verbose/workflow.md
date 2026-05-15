---
name: "meta"
description: "Comprehensive guide to creating and managing workflows using meta-workflow patterns"
version: "1.0"
languages: ["python", "typescript", "markdown"]
subagents: ["orchestrator", "architect"]
---

# Meta-Workflow (Verbose)

## Purpose
This workflow provides a systematic approach to creating, documenting, testing, and iterating on workflows themselves. Use this when you need to formalize a repeatable process or improve existing workflow documentation.

## When to Use This Workflow
- Creating a new workflow from scratch
- Improving existing workflow documentation
- Standardizing team processes
- Ensuring workflow quality and completeness

## Prerequisites
- Understanding of the problem domain
- Access to examples of the process being documented
- Ability to test the workflow with real scenarios
- Version control for workflow files

---

## Steps

### 1. Define Workflow Scope

**Goal:** Clearly articulate what problem the workflow solves and when to use it.

#### 1.1 Identify the Problem
Ask:
- What process is currently ad-hoc or inconsistent?
- What pain points exist in the current approach?
- What mistakes happen when this process is done manually?
- What knowledge needs to be transferred to new team members?

**Example:**
```
Problem: Developers deploy code without proper testing, causing production issues.
Pain point: No standard checklist for pre-deployment verification.
Knowledge gap: New developers don't know all the steps veterans follow.
```

#### 1.2 Define Entry Conditions
Document when someone should use this workflow:

**Good entry conditions:**
- "Use when deploying to production"
- "Use when adding a new API endpoint"
- "Use when investigating a performance regression"

**Bad entry conditions (too vague):**
- "Use when writing code" (too broad)
- "Use sometimes" (unclear)

#### 1.3 Define Exit Conditions (Success Criteria)
What does "done" look like?

**Good exit conditions:**
- "All tests passing, code reviewed, deployed to staging"
- "Root cause identified, fix verified, incident documented"
- "PR approved, merged to main, deployed to production"

**Bad exit conditions:**
- "Everything works" (not measurable)
- "Done when done" (circular)

#### 1.4 List Prerequisites
What must exist before starting this workflow?

**Examples:**
- Tools: Git, Docker, Python 3.11+, pytest
- Permissions: AWS deploy access, database credentials
- Knowledge: Understanding of REST APIs, familiarity with testing frameworks
- Artifacts: Requirements document, approved design, test data

---

### 2. Identify Workflow Steps

**Goal:** Break the process into discrete, actionable steps that can be followed without ambiguity.

#### 2.1 List All Steps (Brain Dump)
Write down every step in the process, no matter how small. Don't organize yet.

**Example (deployment workflow):**
- Run tests
- Check test coverage
- Run linter
- Update version number
- Build Docker image
- Tag Docker image
- Push to registry
- Update deployment config
- Apply deployment
- Verify health checks
- Monitor logs
- Notify team

#### 2.2 Order Steps by Dependency
Identify which steps must happen before others.

**Dependency mapping:**
```
Run tests → Build Docker image → Push to registry → Deploy
Update version → Tag Docker image → Push to registry
Run linter → Build (can run in parallel with tests)
```

**Parallel steps (can happen simultaneously):**
- Run tests + Run linter + Check coverage
- Tag Docker image + Update deployment config

#### 2.3 Identify Decision Points
Where does the workflow branch based on conditions?

**Example decision points:**
```
IF tests fail:
  → Stop workflow, fix tests
  → Do NOT proceed to build

IF coverage < 80%:
  → Optional: Add more tests
  → Required: Document why coverage is low

IF deployment environment == production:
  → Require manual approval
  → Send notification to on-call
ELSE (staging):
  → Auto-deploy
```

#### 2.4 Add Verification Steps
After each major action, add a verification step:

**Pattern:**
```
Step N: Deploy application
Step N+1: Verify deployment succeeded
  - Check health endpoint returns 200
  - Confirm new version in logs
  - Run smoke tests
```

---

### 3. Document Workflow

**Goal:** Create minimal and verbose versions with proper structure and real examples.

#### 3.1 Write Minimal Version (25-50 lines)
Essential steps only, no examples or edge cases.

**Structure:**
```markdown
---
version: "1.0"
languages: ["python"]
subagents: ["code"]
---

# Deployment Workflow (Minimal)

## Steps

### 1. Pre-deployment Checks
- Run all tests
- Check coverage >= 80%
- Run linter

### 2. Build Artifacts
- Update version number
- Build Docker image
- Tag with version and 'latest'

### 3. Deploy
- Push image to registry
- Update deployment config
- Apply to environment
- Verify health checks pass

### 4. Post-deployment
- Monitor logs for errors
- Run smoke tests
- Notify team
```

#### 3.2 Write Verbose Version (200-400 lines)
Full detail with examples, edge cases, troubleshooting.

**Structure:**
```markdown
---
version: "1.0"
languages: ["python"]
subagents: ["code", "debug"]
---

# Deployment Workflow (Verbose)

## Purpose
Deploy applications to staging or production with proper verification.

[Full detailed steps with examples, commands, edge cases]

## Common Mistakes
[List of 5-8 common errors with solutions]

## Troubleshooting
[What to do when things go wrong]
```

#### 3.3 Include YAML Frontmatter
Required fields:
- `name`: Workflow identifier (kebab-case)
- `version`: Semantic version (1.0, 1.1, 2.0)
- `languages`: List of relevant languages
- `subagents`: List of relevant modes/agents

Optional fields:
- `description`: One-line summary
- `tags`: Keywords for searchability

#### 3.4 Add Real Examples (Not Placeholders)
Bad: "Run the command to deploy"
Good: `kubectl apply -f deployment.yaml`

Bad: "Check the logs"
Good: `kubectl logs -f deployment/myapp --tail=100`

---

### 4. Test Workflow

**Goal:** Validate the workflow works with real scenarios and catch gaps.

#### 4.1 Walk Through with Real Scenario
Pick a realistic scenario and execute every step:

**Example:**
```
Scenario: Deploy API service v1.2.3 to staging

Step 1: Pre-deployment checks
- Ran: pytest tests/
- Result: 127 tests passed
- Coverage: 89% (exceeds 80% threshold) ✓
- Linter: ruff check . → no errors ✓

Step 2: Build artifacts
- Updated version in pyproject.toml to 1.2.3 ✓
- Built image: docker build -t myapi:1.2.3 . ✓
- Tagged: docker tag myapi:1.2.3 myapi:latest ✓

[Continue for all steps...]
```

#### 4.2 Identify Unclear Steps
Mark any step where you had to make assumptions or guess:

**Example:**
```
Step 3.2: "Update deployment config"
- UNCLEAR: Where is the deployment config file?
- UNCLEAR: What fields need to be updated?
- UNCLEAR: Is there a template to follow?

→ FIX: Add specific path and example
```

#### 4.3 Test All Decision Branches
If workflow has branches, test each path:

**Example:**
```
Branch 1: Tests pass → proceed to build ✓ TESTED
Branch 2: Tests fail → stop workflow ✓ TESTED
Branch 3: Coverage low → warn but continue ✓ TESTED
Branch 4: Production deploy → manual approval ✓ TESTED
```

#### 4.4 Verify Exit Conditions
After completing workflow, check if success criteria are met:

**Checklist:**
```
Exit conditions for deployment workflow:
- [ ] Application running in target environment
- [ ] Health check endpoint returns 200
- [ ] Logs show no errors for 5 minutes
- [ ] Smoke tests passed
- [ ] Team notified in Slack
```

If any checklist item fails, the workflow is incomplete.

---

### 5. Iterate and Improve

**Goal:** Continuously improve workflow based on real-world usage.

#### 5.1 Gather Feedback from Users
After workflow has been used 3-5 times, ask:

**Questions to ask:**
- Which steps were confusing?
- Where did you get stuck?
- What information was missing?
- Which examples were helpful?
- What would make this easier?

**Feedback collection:**
```
User 1: "Step 3 says 'verify health checks' but doesn't say how"
→ Action: Add specific curl command to check health endpoint

User 2: "I didn't know where to find the deployment config file"
→ Action: Add file path and link to config documentation

User 3: "What if the deploy fails halfway through?"
→ Action: Add rollback section
```

#### 5.2 Identify Common Failure Points
Track where users commonly make mistakes or encounter errors:

**Failure tracking:**
```
Failure: Forgot to update version number (happened 3 times)
→ Fix: Add automated check in pre-deployment step

Failure: Pushed to wrong registry (happened 2 times)
→ Fix: Add verification step showing registry URL before pushing

Failure: Deployed without running tests (happened 1 time)
→ Fix: Make test step mandatory, add automated gate
```

#### 5.3 Add Clarifications or Missing Steps
Based on feedback, update the workflow:

**Before:**
```
### 3. Deploy
- Push image to registry
- Apply deployment
```

**After:**
```
### 3. Deploy

3.1 Push to Registry
Run: `docker push registry.example.com/myapi:1.2.3`
Verify: `docker pull registry.example.com/myapi:1.2.3`
Expected: Image pulls successfully

3.2 Apply Deployment
Run: `kubectl apply -f k8s/deployment.yaml`
Verify: `kubectl get pods | grep myapi`
Expected: Pods show "Running" status within 60 seconds
```

#### 5.4 Version the Workflow
When making significant changes, increment the version:

**Versioning rules:**
- **Patch (1.0 → 1.0.1):** Typo fixes, minor clarifications
- **Minor (1.0 → 1.1):** Added examples, new sections, improved clarity
- **Major (1.0 → 2.0):** Changed steps, different approach, breaking changes

**Changelog example:**
```yaml
---
version: "1.2.0"
changelog:
  - version: "1.2.0"
    date: "2026-04-10"
    changes:
      - "Added rollback section"
      - "Added automated version check"
      - "Improved error handling examples"
  - version: "1.1.0"
    date: "2026-03-15"
    changes:
      - "Added health check verification"
      - "Added smoke test examples"
  - version: "1.0.0"
    date: "2026-03-01"
    changes:
      - "Initial version"
---
```

---

## Workflow Quality Checklist

Before publishing a workflow, verify:

```
Completeness:
- [ ] All steps are actionable (no vague instructions)
- [ ] Entry conditions are clear
- [ ] Exit conditions are measurable
- [ ] Prerequisites are listed
- [ ] Decision points are documented

Examples:
- [ ] At least 1 real example per major step
- [ ] No placeholder text ("run the command", "do the thing")
- [ ] Commands include actual paths/values
- [ ] Example outputs are shown

Testing:
- [ ] Workflow tested with real scenario
- [ ] All decision branches tested
- [ ] Exit conditions verified
- [ ] Edge cases documented

Structure:
- [ ] Valid YAML frontmatter
- [ ] Minimal version exists (25-50 lines)
- [ ] Verbose version exists (200-400 lines)
- [ ] Version number included
- [ ] Clear headings and hierarchy
```

---

## Common Workflow Patterns

### Pattern 1: Linear Workflow
Steps happen in strict sequence, no branching.

**Example:** Build → Test → Deploy

**Use when:** Process is straightforward with no conditional logic.

### Pattern 2: Branching Workflow
Different paths based on conditions.

**Example:**
```
IF environment == production:
  → Manual approval required
ELSE:
  → Auto-deploy
```

**Use when:** Different rules apply in different contexts.

### Pattern 3: Parallel Workflow
Multiple steps happen simultaneously.

**Example:** Run unit tests + Run linter + Run type checker (all in parallel)

**Use when:** Steps are independent and can save time running concurrently.

### Pattern 4: Iterative Workflow
Repeat steps until condition met.

**Example:**
```
WHILE tests failing:
  → Fix code
  → Run tests again
```

**Use when:** Process requires refinement until success criteria met.

---

## Meta-Workflow Example: Creating a Code Review Workflow

**Step 1: Define Scope**
- Problem: Code reviews inconsistent, some PRs approved without proper checks
- Entry: When PR is opened
- Exit: PR approved or changes requested
- Prerequisites: Git, GitHub access, understanding of codebase conventions

**Step 2: Identify Steps**
1. Read PR description
2. Check automated CI passes
3. Review code changes file by file
4. Check for tests
5. Check for documentation
6. Leave review comments
7. Approve or request changes

**Dependencies:**
- CI must pass before review starts
- All comments addressed before approval

**Decision points:**
- IF CI failing → Request fixes, do not review code yet
- IF no tests → Request tests
- IF breaking change → Require documentation

**Step 3: Document**
- Minimal version: 6 steps, no examples
- Verbose version: Full detail with checklist, examples of good/bad code, common issues to watch for

**Step 4: Test**
- Walk through 3 real PRs using the workflow
- Identified missing step: "Check for security issues"
- Added that step to workflow

**Step 5: Iterate**
- After 2 weeks, gathered feedback
- Users wanted examples of constructive comments
- Added "How to Leave Helpful Comments" section
- Incremented version to 1.1.0
