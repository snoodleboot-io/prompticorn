---
name: data-model-discovery
description: Essential questions to ask before designing a data model
languages: [all]
subagents: [architect/data-model]
tools_needed: []
---

## Data Model Discovery Questions

Before designing any data model, ask these questions:

1. **What are the core entities and their relationships?**
   - Identify nouns in requirements
   - Map relationships (1:1, 1:many, many:many)

2. **What are the most common read patterns?**
   - Which queries will run most frequently?
   - What filters/sorts are needed?

3. **What are the most common write patterns?**
   - Insert frequency and volume
   - Update patterns and triggers

4. **Are there soft-delete, audit trail, or versioning requirements?**
   - Do records need to be recoverable?
   - Is history tracking required?

5. **Any known scale constraints?**
   - Expected row counts
   - Request volume (reads/writes per second)
   - Geographic distribution

### Usage
- Ask all questions before producing designs
- Document answers in design doc
- Use answers to inform indexing and denormalization decisions


