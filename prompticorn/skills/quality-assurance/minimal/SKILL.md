# Quality Assurance (Minimal)

## Purpose
Make quality a measured property of the delivery system rather than an opinion
held at the end of a sprint.

## Core Techniques

### 1. Measure Quality With Four Numbers
| Metric | Definition | Signal |
|---|---|---|
| Defect escape rate | Defects found in production ÷ total defects found, per release | How much your pre-release testing actually catches |
| Change failure rate | Deployments causing degradation or rollback ÷ all deployments | Whether the release path is safe |
| MTTR | Median wall-clock from customer impact starting to impact ending | How fast you recover when it isn't |
| Defect age | Median days from introduction to detection | How far left your feedback has actually shifted |

Escape rate is the one that exposes theatre: a team with 4,000 tests and a 60%
escape rate is testing the wrong things. Count defects consistently — decide
whether a rolled-back deploy is one defect or zero, write it down, and stop
relitigating it.

### 2. Shift Left With Specific Gates
"Test earlier" is a slogan until it names a gate and a stage:

- **Pre-commit:** formatter, linter, type checker, secret scan.
- **Pre-merge:** unit and contract tests, coverage on changed lines, migration
  runs forward and backward on a copy of production schema.
- **Post-merge:** integration suite against real dependencies in containers.
- **Pre-release:** smoke suite against staging with production-scale data.
- **Post-release:** synthetic checks and error-budget burn alerting.

Each stage is faster and cheaper than the next. A type error caught by a
pre-commit hook costs seconds; the same error found in staging costs a build, a
deploy, and a context switch.

### 3. Prioritise by Risk, Not by Coverage
Risk = likelihood of failure × impact if it fails. Score both 1–5 and test the
top-right corner hard.

| Area | Likelihood | Impact | Risk | Test depth |
|---|---|---|---|---|
| Payment capture | 3 | 5 | 15 | Unit + contract + E2E + manual exploratory each release |
| Auth / session | 2 | 5 | 10 | Unit + integration + security review |
| Search ranking | 4 | 2 | 8 | Unit + offline eval set |
| Admin CSV export | 2 | 2 | 4 | One happy-path integration test |
| Marketing footer | 1 | 1 | 1 | None; visual diff catches it |

Likelihood rises with change frequency, code age, complexity, and defect
history. Uniform coverage targets spend the same effort on the footer as on
payment capture, which is how teams get to 85% coverage and still ship
checkout bugs. See `testing-strategies` for the test-type mix itself.

### 4. Charter Exploratory Sessions
Automation checks what you already thought of. Exploratory testing finds what you
didn't. Make it a time-boxed session with a written charter, not "click around":

> **Charter:** Explore multi-currency refunds on partially-shipped orders,
> using accounts with mixed-currency payment methods, to discover rounding and
> ledger-balance errors. **Time-box:** 90 min.
> **Notes:** what was tried, what was observed, bugs raised, coverage gaps found,
> follow-up questions.

Charter the areas where the spec is thin, the risk is high, or the workflow
crosses several systems — precisely where scripted tests are weakest.

### 5. Write Entry/Exit Criteria That Can Actually Fail
A criterion no release has ever failed is decoration. Make them binary and
enforced:

- **Entry to release testing:** all merge-gate checks green; migrations rehearsed
  on a production-sized copy; feature flags default off; rollback documented.
- **Exit:** zero open sev-1/sev-2 defects; escape-rate trend not worsening for
  two releases; smoke suite green against staging; on-call briefed on what
  changed and how to turn it off.

"Rollback documented" means someone wrote the command. If nothing has ever been
blocked by your exit criteria, you have a checklist, not a gate.

### 6. Delete the QA Phase
A testing phase at the end batches defects to the point of maximum repair cost,
lets the author lose all context, creates a queue that gets compressed whenever
the date slips, and makes quality one team's job. Replace it with quality
gates inside the flow: definition of ready, tests written with the code, review
covering testability, progressive delivery behind flags, canary plus automated
rollback, and QA specialists embedded as risk analysts and exploratory testers
rather than as a downstream inspection step.

## Warning Signs

- Quality reported as a coverage percentage and nothing else
- No idea what fraction of defects reach customers
- A hardening or stabilisation sprint that recurs every release
- Exit criteria that have never blocked a release
- Testing effort spread evenly regardless of blast radius
- Exploratory testing that means unscripted clicking with no charter or notes
- Bugs found in staging that a unit test could have caught at commit time
- "QA signed off" used as the record of quality, with no measurement behind it
- Flaky tests routinely re-run until green (see `flaky-test-remediation`)
