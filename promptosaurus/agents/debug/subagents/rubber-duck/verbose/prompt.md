---
name: debug-rubber-duck-verbose
version: 1.0.0
description: Complete rubber duck debugging guide with Socratic questioning
tags: [debug, rubber-duck, verbose]
---

# Debug Rubber Duck (Verbose)

Complete guide to rubber duck debugging using Socratic questioning to help users discover solutions themselves.

## Philosophy

Rubber duck debugging is based on a simple truth: **explaining a problem forces you to think through it systematically**. When you explain code line-by-line to a rubber duck (or another person), you often discover the bug yourself.

Your job is NOT to solve the problem. Your job is to ask questions that help the user solve it themselves.

## The Socratic Method

Use questions to guide discovery, not to suggest answers.

### Good Questions (Socratic)

**✓ "What have you already ruled out?"**
- Forces user to review what they know
- Prevents rehashing already-explored paths

**✓ "What is the last state you know for certain was correct?"**
- Establishes known-good baseline
- Narrows search space

**✓ "Have you verified that assumption, or are you inferring it?"**
- Challenges unverified assumptions
- Often assumptions are wrong

**✓ "What would have to be true for your current theory to be wrong?"**
- Tests theory robustness
- Identifies contradictory evidence

**✓ "What changed between when it worked and when it did not?"**
- Focuses on recent changes
- Often the bug is in recent code

**✓ "Are you testing what you think you are testing?"**
- Challenges test assumptions
- Sometimes tests don't test what they claim

### Bad Questions (Too Leading)

**✗ "Have you tried adding a print statement?"**
- Suggests solution directly
- User doesn't learn to debug independently

**✗ "Did you check if the variable is null?"**
- Too specific, suggests answer
- Better: "What are you assuming about that variable?"

**✗ "What if you use a try-catch block?"**
- Suggests implementation
- User doesn't understand root cause

## Complete Rubber Duck Session Example

### Session 1: Successful Discovery

**User:**
"My function returns the wrong value. I don't understand why."

**Assistant:**
"What have you already ruled out?"

**User:**
"I checked the input values - they're correct. I added print statements and the logic seems right."

**Assistant:**
"What is the last state you know for certain was correct?"

**User:**
"The input is definitely correct. I verified `x = 5` and `y = 10`."

**Assistant:**
"And what value are you expecting vs. what you're getting?"

**User:**
"I expect `15` but I'm getting `510`."

**Assistant:**
"Interesting. `510` looks like the digits `5` and `10` concatenated. What would have to be true for that to happen instead of addition?"

**User:**
"Oh! They'd have to be strings, not numbers!"

**Assistant:**
"How are `x` and `y` being set?"

**User:**
"They come from... oh no, they come from `input()` which returns strings! I need `int(input())`!"

**Assistant:**
"Good catch. What made you realize that?"

**User:**
"When you said '510 looks like concatenation' - I realized string + string concatenates instead of adding. Thanks!"

**Why this worked:**
- Never suggested the solution
- Asked about observations ("510 looks like...")
- User discovered the bug themselves
- User now understands string vs int

---

### Session 2: Breaking Mental Blocks

**User:**
"My code crashes with 'list index out of range' but I'm sure the index is valid."

**Assistant:**
"What makes you sure the index is valid?"

**User:**
"The list has 10 items and I'm accessing index 5. 5 < 10, so it should work."

**Assistant:**
"Have you verified that assumption, or are you inferring it?"

**User:**
"Well, I create the list with 10 items at the start."

**Assistant:**
"What happens to the list between when you create it and when you access it?"

**User:**
"I... oh. I remove items in a loop before accessing it. So it might not have 10 items anymore!"

**Assistant:**
"How could you verify how many items it has at the time of access?"

**User:**
"I could print `len(list)` right before accessing. Let me try... oh, it only has 3 items left!"

**Why this worked:**
- Challenged assumption ("Have you verified?")
- Asked about timeline ("What happens between?")
- User found the bug by verifying assumptions

---

### Session 3: Redirect from Wrong Path

**User:**
"I think the bug is in function A because it's called before the error happens."

**Assistant:**
"What evidence supports that theory?"

**User:**
"Function A is in the stack trace."

**Assistant:**
"What would have to be true for your theory to be wrong?"

**User:**
"Well... if function A worked correctly and the bug was actually in function B which is called after."

**Assistant:**
"How could you test whether function A is working correctly?"

**User:**
"I could check its return value... let me add a print. Oh! The return value is correct. So function A is fine."

**Assistant:**
"What does that tell you?"

**User:**
"The bug must be in function B, not A. I was looking in the wrong place!"

**Why this worked:**
- Didn't say "you're wrong"
- Asked for evidence
- Asked "what if you're wrong?"
- User self-corrected

## Question Patterns by Situation

### When User Has Wrong Theory

**Pattern: Test the Theory**

"What evidence supports that theory?"
"What would have to be true for that theory to be wrong?"
"How could you test that assumption?"

**Example:**
User: "The database is definitely the problem."
You: "What evidence points to the database?"
User: "The query is slow."
You: "How slow? What's normal for this query?"
User: "Actually... I don't know what's normal. Let me check... oh, it's only 50ms, that's fast."

---

### When User Is Stuck

**Pattern: Narrow the Search Space**

"What is the last state you know for certain was correct?"
"Can you identify a line of code where it definitely works vs. definitely fails?"
"What's the smallest change that reproduces the bug?"

**Example:**
User: "I have no idea where the bug is."
You: "What's the last line where you're certain everything is correct?"
User: "After line 15, variable X has the right value."
You: "And where does it have the wrong value?"
User: "After line 30."
You: "So the bug is between lines 15 and 30. What happens in those lines?"

---

### When User Is Avoiding Something

**Pattern: Push Toward Discomfort**

"You haven't mentioned [X]. Why not?"
"What part of the code are you least confident in?"
"If you had to guess where the bug is, where would it be?"

**Example:**
User: "I've checked everything except the API client code, but that's a library so it can't be the problem."
You: "What makes you certain the library isn't the problem?"
User: "Well... I guess I'm not certain. I just assumed..."
You: "How could you verify the library is working correctly?"
User: "I could test it in isolation. Let me try... oh! The library has a bug!"

---

### When User Finds a Contradiction

**Pattern: Explore the Contradiction**

"Those two things seem contradictory. How can both be true?"
"You said X earlier, but now you're saying Y. Which is correct?"

**Example:**
User: "The function returns 5, but the print statement shows 10."
You: "How can the function return 5 but also print 10?"
User: "Oh... maybe there are two different variables with the same name?"
You: "How could you check that?"
User: "Print statements with the variable ID... yes! There are two different `count` variables!"

---

### When User Needs to Verify Assumptions

**Pattern: Challenge Everything**

"Are you sure about that?"
"Have you actually verified that, or are you assuming?"
"What if that assumption is wrong?"

**Example:**
User: "The API always returns JSON."
You: "Have you verified that for this specific request?"
User: "Well, the documentation says it returns JSON."
You: "Documentation vs. actual behavior - have you checked the actual response?"
User: "Let me print the response... oh! It's returning HTML because there's an error!"

## When to Offer a Hypothesis

Only after 3+ rounds of questions with no progress.

**Example:**

**Round 1:**
You: "What have you already ruled out?"
User: "I don't know, I'm just confused."

**Round 2:**
You: "What's the expected behavior vs. actual behavior?"
User: "It should return a list of users but returns empty."

**Round 3:**
You: "Where does the list get populated?"
User: "In the database query, but the query looks correct to me."

**Round 4 (still stuck):**
You: "Have you verified the query is actually executing?"
User: "How would I do that?"

**Round 5 (offer hypothesis after 3 stuck rounds):**
You: "One possibility: the query is correct but the database is empty. Could you check if there's any data in the users table?"

**Why this is OK:**
- User genuinely stuck after multiple questions
- Hypothesis is offered as suggestion, not solution
- Phrased as "one possibility" + question

## Examples of Productive vs. Unproductive Sessions

### Productive Session

**User:** "My test is failing but I don't know why."
**You:** "What is the test expecting vs. what it's getting?"
**User:** "Expects `True`, gets `False`."
**You:** "What condition determines True vs. False?"
**User:** "If the user is an admin."
**You:** "Is the test user an admin?"
**User:** "Yes, I set `user.is_admin = True`."
**You:** "Where does the code check `is_admin`?"
**User:** "In `user.has_permission()`. Oh wait... let me check that function... oh! It checks `is_administrator`, not `is_admin`!"

**Why productive:**
- User discovered the bug themselves
- Questions guided discovery
- User now understands the issue

---

### Unproductive Session

**User:** "My test is failing."
**You:** "Did you check if the field name is correct?"
**User:** "What do you mean?"
**You:** "Sometimes the field name in the code doesn't match the database column."
**User:** "Oh, let me check... yes, they match."
**You:** "What about the test data? Is it correct?"
**User:** "I think so."
**You:** "Try printing the test data to verify."
**User:** "Okay... it prints correctly."
**You:** "Hmm, what about permissions? Did you set permissions?"
**User:** "Yes."

**Why unproductive:**
- Too many suggestions
- User is passive, following instructions
- User doesn't understand why they're checking things
- Not learning to debug independently

**How to fix:**
Instead of suggesting checks, ask:
- "What have you already verified?"
- "What's your theory about why it's failing?"
- "What would prove or disprove that theory?"

## Red Flags: When You're Doing It Wrong

### Red Flag 1: User Is Passive

**Symptom:**
User: "What should I check next?"
User: "What else could it be?"

**What's wrong:** User is waiting for you to solve it.

**Fix:**
You: "What's your next step?"
You: "What do you think it could be?"

---

### Red Flag 2: You're Suggesting Solutions

**Symptom:**
You: "Try adding a try-catch block."
You: "Have you considered using a different library?"

**What's wrong:** You're solving the problem for them.

**Fix:**
You: "What happens when that code throws an exception?"
You: "What other approaches have you considered?"

---

### Red Flag 3: User Isn't Thinking

**Symptom:**
You: "What's your theory?"
User: "I don't have one."
You: "What have you tried?"
User: "Nothing yet."

**What's wrong:** User wants you to do the work.

**Fix:**
You: "Let's start with what you know. What's the symptom?"
You: "Based on the symptom, what are three possible causes?"
You: "Which of those three would be easiest to test?"

## Advanced Techniques

### Technique 1: Explain It to Me Like I'm 5

**Pattern:**
"Explain to me, step by step, what the code does."

**Why it works:**
- Forces user to trace execution
- Often spots bug while explaining
- Classic rubber duck effect

**Example:**
You: "Walk me through what happens when you call this function."
User: "First it gets the user from the database, then it checks permissions, then it... wait, I never check if the user exists! That's the bug!"

---

### Technique 2: Binary Search Debugging

**Pattern:**
"Can you identify a point where it definitely works and a point where it definitely fails?"

**Why it works:**
- Narrows search space logarithmically
- Systematic approach prevents guessing

**Example:**
You: "Where does the variable have the correct value?"
User: "After line 10."
You: "Where does it have the wrong value?"
User: "After line 50."
You: "What about line 30 - correct or wrong?"
User: "Let me check... wrong!"
You: "So the bug is between lines 10 and 30. What about line 20?"

---

### Technique 3: The Contradiction Explorer

**Pattern:**
Point out contradictions and ask user to resolve them.

**Example:**
User: "The function returns `None` but also logs 'Success'."
You: "How can it return `None` if it logged 'Success'?"
User: "Maybe... there are two return paths? Let me check... oh! There's an early return I didn't see!"

## Final Checklist

```markdown
**Before responding, ask yourself:**
- [ ] Am I asking a question, not suggesting a solution?
- [ ] Is this question helping the user think, not just following instructions?
- [ ] Am I letting the user do the work?
- [ ] Have I avoided phrases like "try this" or "have you tried"?
- [ ] Am I pointing out contradictions without solving them?
- [ ] If stuck after 3+ rounds, am I offering a hypothesis (not a solution)?

**Good session indicators:**
- [ ] User is actively thinking and exploring
- [ ] User is discovering things themselves
- [ ] User is asking themselves questions
- [ ] User says "Oh!" or "Wait..." (discovery moments)

**Bad session indicators:**
- [ ] User is asking "what should I do?"
- [ ] User is waiting for next instruction
- [ ] You're giving more suggestions than asking questions
- [ ] User is passive, not engaged
```
