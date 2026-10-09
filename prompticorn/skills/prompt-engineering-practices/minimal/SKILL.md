# Prompt Engineering Practices (Minimal)

## Purpose
Get reliable, parseable behavior out of a model in production — where the same prompt runs a million times against inputs nobody reviewed, and a 2% format failure rate is an incident.

## Core Techniques

### 1. Specify the Output Contract Before Touching the Wording
Most reported "prompt problems" are unspecified output contracts. The complaint is "the model is inconsistent"; the reality is that the prompt never said what shape the answer must take, so the model picked a different reasonable shape each time.

| Symptom blamed on the model | Actual cause | Fix |
|---|---|---|
| "Sometimes it adds a preamble" | No statement that output is only the object | Constrained/structured output |
| "It wraps JSON in a code fence" | Free-text generation, fence is conventional | Schema-enforced decoding |
| "It invents a status value" | Field typed as string, not an enum | Enum in the schema |
| "It says it can't answer, and that breaks parsing" | No legal way to decline inside the contract | Add an `uncertain` variant to the schema |

Define the schema first. Then the prompt only has to explain the *task*, not the *format*.

### 2. Never Parse Free Text You Could Have Constrained
Regex over prose fails on the long tail: a translated field name, a trailing period, a number written as "three", an em dash where a hyphen was expected. It fails on 1-2% of traffic, which is invisible in a demo and constant at scale.

```python
schema = {"type": "object", "required": ["category", "confidence"],
          "properties": {
            "category": {"enum": ["billing", "technical", "account", "uncertain"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1}},
          "additionalProperties": False}
```

Use the provider's structured-output or tool-calling mode so the schema constrains decoding rather than merely describing it. If you only have free text, validate against the schema anyway, and treat a validation failure as a first-class outcome with a repair retry — not an exception that reaches the user.

Include `uncertain` (or `null`, or an `insufficient_context` variant) in every enum. A model with no legal way to say "I don't know" will pick the closest wrong label, and it will do so confidently.

### 3. Order the Prompt by Stability, Not by Narrative
```
[ role and task ][ rules ][ output contract ][ few-shot examples ]   <- static, cacheable
[ retrieved context ][ the user's input ]                            <- volatile, last
```

Static first makes the prefix cacheable and keeps the instructions from being buried. The user's input goes last, clearly delimited, and is never interpolated into the instruction block — data placed inside the instructions is read as instructions, which is both an injection vector and a plain correctness bug when a document happens to contain the word "ignore".

Delimit untrusted input explicitly (`<document>…</document>`) and state in the rules that content inside the delimiters is data to analyze, never instructions to follow.

### 4. Choose Instructions vs Examples by What the Model Got Wrong
| The failure | Add | Why |
|---|---|---|
| Wrong format or structure | Schema, then one example | Format is a contract, not a suggestion |
| Right shape, wrong judgment on edge cases | Examples of those edge cases | Boundaries are easier to show than to describe |
| A rule violated occasionally | An explicit instruction, stated positively | "Reply in English" beats "don't reply in other languages" |
| Style, tone, register | Examples | Nearly impossible to specify in prose |
| Rule applied too aggressively | A counter-example | Balances the pull of the existing ones |

Prose instructions scale poorly: a 40-rule prompt has rules that contradict each other and rules the model reliably ignores because they sit in the middle. Examples cost tokens on every call but encode boundaries precisely. The practical rule — describe the rule once, then demonstrate the edge cases.

### 5. Select Few-Shot Examples From Failures, Not From Successes
Three or four examples usually capture most of the available gain. Which three matters more than how many.

- Draw them from real production inputs, especially ones the prompt currently gets wrong.
- Cover the decision boundary, not the obvious center — the ambiguous ticket, not the clearly-billing one.
- Balance the label distribution. Four positives and one negative teaches the model the prior, and it will over-predict the majority class.
- Keep format byte-identical across examples; inconsistent example formatting is a leading cause of inconsistent output.
- Check for leakage: an example that happens to match an eval item makes your eval numbers meaningless.

### 6. Treat Prompts as Code: Versioned, Reviewed, Rollable-Back
A prompt is program logic that ships to production. Give it what any other logic gets.

```
prompts/
  support_classify/
    v3.md        # the prompt template
    schema.json  # the output contract
    evals.jsonl  # labeled cases, including every past regression
```

Version the prompt and log the version with every call, so a quality regression can be attributed. Review prompt diffs — a one-word change ("summarize" to "briefly summarize") can move output length by half. Run the eval set in CI and block on regressions. Roll back by config, not by redeploy, because the fastest fix for a bad prompt at 2am is reverting to the previous version in seconds.

The failure this prevents is the common one: prompts edited live in a console, no history, no eval, and nobody able to answer "what changed?" when quality drops on a Tuesday.

## Warning Signs

- The prompt describes the output format in prose instead of enforcing a schema
- Regexes or string splitting over model prose in the parsing path
- No `uncertain` / `none` option in any enum the model must choose from
- User input interpolated directly into the instruction block, undelimited
- Fifteen-plus prose rules accreted over time, never pruned, some contradictory
- Few-shot examples invented by the prompt author rather than drawn from production
- Examples all of one class, or formatted inconsistently with each other
- Prompts stored as string literals inline in application code
- No prompt version in logs, so regressions cannot be attributed to a change
- No eval set, so "it seems better" is the entire acceptance test
