# architect-data-model.md
# Behavior when the user asks to design a data model or schema.

When the user asks to design a data model, schema, or database structure:

1. Read what the user provided and core-conventions.md for the database type.
   Only ask questions if the answer would meaningfully change the schema design
   and cannot be inferred from context.

   Worth asking if missing:
   - Primary read patterns (what queries will be most common)?
   - Soft-delete, audit trail, or versioning requirements?
   - Known scale constraints?

   Not worth asking if already clear from context:
   - What entities exist — the user just described them
   - Which database — read from core-conventions.md

2. Produce:
   - Entity definitions: name, fields, types, nullability, defaults, constraints
   - Relationship diagram in Mermaid ERD format
   - Index recommendations based on the stated query patterns
   - Denormalization or caching recommendations with rationale
   - Migration file skeleton (up + down)
   - Open questions or tradeoffs needing a decision before implementing

3. Do NOT generate ORM code — schema design only until the user approves.

Mermaid ERD format:
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