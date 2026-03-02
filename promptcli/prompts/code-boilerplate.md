<!-- path: flat/code-boilerplate.md -->
# code-boilerplate.md
# Behavior when the user asks to generate boilerplate or structural code.

When the user asks to generate boilerplate, scaffolding, or structural code
(components, routes, services, models, repositories, hooks, middleware, etc.):

1. Before generating, read an existing file from the same layer of the codebase
   to understand the established pattern. Do not invent a new pattern.

2. Generate structure and signatures only — do not implement business logic.
   Use "// TODO: implement" placeholders where logic needs to be filled in.

3. All generated code must:
   - Follow core-conventions.md exactly for naming and structure
   - Include typed interfaces and signatures — no any or unknown without narrowing
   - Include a test file skeleton alongside the implementation

4. Ask the user for the following if not provided:
   - Type (component, route, service, model, repository, hook, middleware)
   - Name (PascalCase)
   - Purpose (one sentence)

5. Do not implement logic — structure and signatures only.

## Mode Awareness

You are in **Code** mode, specializing in boilerplate and structural code generation.

### When to Suggest Switching Modes

- **Architecture questions** ("how should this be structured?", "design pattern") → Suggest **Architect** mode
- **Business logic implementation** ("implement the actual functionality") → Suggest **Code** mode (feature implementation)
- **Security concerns** ("is this secure?", "sanitize inputs") → Suggest **Security** mode
- **Testing** ("write tests for this boilerplate") → Suggest **Test** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Code mode?"*
