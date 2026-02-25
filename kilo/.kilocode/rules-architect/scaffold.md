# architect-scaffold.md
# Behavior when the user asks to scaffold or start a new project.

When the user asks to scaffold a new project or set up a project structure:

1. First, read core-conventions.md and extract everything already known:
   language, framework, runtime, structure, package manager, etc.
   Do NOT ask about anything already defined there or already described
   by the user in their message.

   Only ask if something is genuinely missing AND would meaningfully change
   the structure. Acceptable questions:
   - Is this a monorepo or single service? (if not clear)
   - Any external services to integrate with? (if not mentioned)
   - Any compliance or constraint requirements? (if not mentioned)

   If you have enough to propose a structure, skip questions entirely
   and go straight to step 2.

2. Propose:
   - A folder structure with a one-line rationale per top-level directory
   - Config files to create (tsconfig, .env.example, Dockerfile, CI workflow, etc.)
   - A README.md skeleton with placeholder sections

3. Ask for confirmation. Then generate all files.

4. Follow core-conventions.md for all naming and structure decisions.