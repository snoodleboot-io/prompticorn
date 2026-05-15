---
name: "data-model"
description: Design database schema with entities, relationships, and indexes
steps:
- Gather requirements
- Design schema
- Document design
- Get approval
---

## Steps

### Step 1: Gather requirements

Ask before designing:
- Core entities and relationships?
- Common read/write patterns?
- Soft-delete, audit trail, or versioning needs?
- Scale constraints (rows, request volume, geography)?

### Step 2: Design schema

Produce:
- Entity definitions (name, fields, types, nullability, defaults, constraints)
- Mermaid ERD showing relationships
- Index recommendations based on query patterns
- Denormalization/caching suggestions with rationale
- Migration skeleton (up + down)
- Open questions or tradeoffs

### Step 3: Document design

Use Mermaid ERD format:
```
erDiagram
    USER {
        uuid id PK
        string email
        timestamp created_at
    }
    ORDER {
        uuid id PK
        uuid user_id FK
        string status
    }
    USER ||--o{ ORDER : "places"
```

### Step 4: Get approval

- Do NOT generate ORM code until approved
- Use database from Core Conventions
- Wait for user sign-off before implementation
