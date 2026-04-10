---
languages: ["python", "typescript", "javascript"]
subagents: ["code"]
---

# Boilerplate Generation Workflow (Comprehensive)

## Overview

Boilerplate generation automates creation of repetitive code structures while maintaining project conventions. This workflow ensures consistency, reduces errors, and speeds up development.

**Key Principle:** Generate structure and signatures only—never implement business logic in generated code.

---

## Phase 1: Pattern Recognition

### 1.1 Identify Repetitive Structures

Look for files that share similar patterns:

**Common boilerplate patterns:**
- **Models/Entities:** Data classes with fields, validation, serialization
- **Controllers/Handlers:** HTTP request handlers with similar CRUD patterns
- **Services:** Business logic layers with common operation patterns
- **Repositories:** Data access layers with CRUD operations
- **Tests:** Test suites mirroring implementation files
- **API Routes:** Endpoint definitions following RESTful patterns

**Questions to ask:**
1. Are there 3+ files with nearly identical structure?
2. Do they differ only in naming and specific types/fields?
3. Is the pattern likely to repeat for new features?

If yes to all three, boilerplate generation is appropriate.

### 1.2 Document the Pattern

Create a clear description of what stays constant vs. what varies:

**Example: RESTful Controller Pattern**

**Constants (same every time):**
- HTTP method decorators (@get, @post, @put, @delete)
- Error handling structure
- Response envelope format
- Authentication middleware

**Variables (changes per resource):**
- Resource name (User, Product, Order)
- Field names and types
- Validation rules
- Related entities

---

## Phase 2: Study Existing Code

### 2.1 Find and Read Examples

Before generating ANY boilerplate, read 2-3 existing files from the same architectural layer:

```bash
# Python examples
find src/ -name "*_controller.py" | head -3 | xargs cat

# TypeScript examples
find src/ -name "*Service.ts" | head -3 | xargs cat

# Test examples
find tests/ -name "test_*.py" | head -3 | xargs cat
```

### 2.2 Extract Conventions

Document observed patterns:

**Naming conventions:**
- File naming: `user_controller.py` (snake_case) vs `UserService.ts` (PascalCase)
- Class naming: `UserController` vs `ProductController`
- Method naming: `get_by_id()` vs `getById()`

**Import patterns:**
```python
# Python pattern observed
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserUpdate
```

```typescript
// TypeScript pattern observed
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';
```

**Structural patterns:**
- Inheritance: Do controllers extend BaseController?
- Decorators: What decorators are used (@Injectable, @route)?
- Error handling: Try/catch blocks? Exceptions?
- Dependency injection: Constructor params? Service locator?

### 2.3 Note Common Pitfalls

From existing code, identify what NOT to do:
- Hardcoded values that should be parameterized
- Missing type annotations
- Inconsistent error handling
- Missing tests

---

## Phase 3: Template Creation

### 3.1 Structure-Only Generation

**Golden Rule:** Generate signatures and structure ONLY. No business logic.

**Python controller boilerplate example:**

```python
# src/controllers/{{resource}}_controller.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.{{resource}} import {{Resource}}
from app.schemas.{{resource}} import {{Resource}}Create, {{Resource}}Update, {{Resource}}Response

router = APIRouter(prefix="/{{resource_plural}}", tags=["{{resource_plural}}"])


@router.get("/", response_model=List[{{Resource}}Response])
def list_{{resource_plural}}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve list of {{resource_plural}}.
    
    # TODO: implement filtering logic
    # TODO: implement sorting
    # TODO: implement pagination
    """
    raise NotImplementedError("Implement list operation")


@router.get("/{id}", response_model={{Resource}}Response)
def get_{{resource}}(id: int, db: Session = Depends(get_db)):
    """
    Retrieve single {{resource}} by ID.
    
    # TODO: implement database query
    # TODO: handle not found case
    """
    raise NotImplementedError("Implement get operation")


@router.post("/", response_model={{Resource}}Response, status_code=201)
def create_{{resource}}(
    {{resource}}: {{Resource}}Create,
    db: Session = Depends(get_db)
):
    """
    Create new {{resource}}.
    
    # TODO: implement validation
    # TODO: implement database insert
    # TODO: handle uniqueness constraints
    """
    raise NotImplementedError("Implement create operation")


@router.put("/{id}", response_model={{Resource}}Response)
def update_{{resource}}(
    id: int,
    {{resource}}: {{Resource}}Update,
    db: Session = Depends(get_db)
):
    """
    Update existing {{resource}}.
    
    # TODO: implement existence check
    # TODO: implement update logic
    # TODO: handle not found case
    """
    raise NotImplementedError("Implement update operation")


@router.delete("/{id}", status_code=204)
def delete_{{resource}}(id: int, db: Session = Depends(get_db)):
    """
    Delete {{resource}} by ID.
    
    # TODO: implement existence check
    # TODO: implement delete logic
    # TODO: handle cascading deletes
    """
    raise NotImplementedError("Implement delete operation")
```

**TypeScript service boilerplate example:**

```typescript
// src/services/{{Resource}}Service.ts
import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { {{Resource}} } from '../entities/{{resource}}.entity';
import { Create{{Resource}}Dto, Update{{Resource}}Dto } from '../dto/{{resource}}.dto';

@Injectable()
export class {{Resource}}Service {
  constructor(
    @InjectRepository({{Resource}})
    private readonly {{resource}}Repository: Repository<{{Resource}}>,
  ) {}

  async findAll(skip: number = 0, limit: number = 100): Promise<{{Resource}}[]> {
    // TODO: implement query with pagination
    // TODO: add filtering support
    throw new Error('Not implemented');
  }

  async findOne(id: number): Promise<{{Resource}}> {
    // TODO: implement database query
    // TODO: throw NotFoundException if not found
    throw new Error('Not implemented');
  }

  async create(create{{Resource}}Dto: Create{{Resource}}Dto): Promise<{{Resource}}> {
    // TODO: validate input
    // TODO: create entity instance
    // TODO: save to database
    throw new Error('Not implemented');
  }

  async update(id: number, update{{Resource}}Dto: Update{{Resource}}Dto): Promise<{{Resource}}> {
    // TODO: find existing entity
    // TODO: merge updates
    // TODO: save changes
    throw new Error('Not implemented');
  }

  async remove(id: number): Promise<void> {
    // TODO: find existing entity
    // TODO: handle cascading deletes
    // TODO: remove from database
    throw new Error('Not implemented');
  }
}
```

### 3.2 Placeholder Strategy

Use clear, searchable placeholders:

**Good placeholders:**
```python
# TODO: implement validation logic
# FIXME: handle edge case when user is deleted
# NOTE: This assumes single-threaded access
raise NotImplementedError("Implement pagination")
```

**Bad placeholders:**
```python
# ... implement here ...
pass  # (no explanation)
# do stuff
```

**TypeScript/JavaScript placeholders:**
```typescript
throw new Error('Not implemented: add validation logic');
console.warn('TODO: implement caching');
return null as any; // FIXME: proper type inference
```

### 3.3 Type Safety

**All generated code MUST be fully typed:**

**Python (use type hints):**
```python
def get_user(user_id: int, db: Session) -> Optional[User]:
    # NOT: def get_user(user_id, db):
    pass
```

**TypeScript (explicit return types):**
```typescript
async findOne(id: number): Promise<User> {
  // NOT: async findOne(id) {
  throw new Error('Not implemented');
}
```

**Avoid:**
- Python: Missing type hints, using `Any` without justification
- TypeScript: Using `any`, implicit return types, untyped parameters

---

## Phase 4: Parameterization

### 4.1 Identify Variables

List all values that change between instances:

**Example: User → Product transformation**

| Variable | User Example | Product Example |
|----------|--------------|-----------------|
| Resource name (singular) | User | Product |
| Resource name (plural) | users | products |
| Primary key type | int | UUID |
| Unique fields | email | sku |
| Related entities | Orders, Address | Category, Supplier |
| Validation rules | email format | price > 0 |

### 4.2 Template Variable Format

Use clear, consistent variable naming:

**Mustache-style (recommended):**
```python
# {{resource}} → user
# {{Resource}} → User
# {{RESOURCE}} → USER
# {{resource_plural}} → users
```

**Example substitution:**
```python
# Template
class {{Resource}}Controller:
    def get_{{resource}}(self, {{resource}}_id: int) -> {{Resource}}:
        pass

# After substitution (resource=product)
class ProductController:
    def get_product(self, product_id: int) -> Product:
        pass
```

### 4.3 Code Generation Tools

**Option 1: Manual templating (simple cases)**
```bash
# Use sed for simple replacements
sed 's/{{resource}}/product/g' template.py > product_controller.py
```

**Option 2: Template engines (complex cases)**

**Jinja2 (Python):**
```python
from jinja2 import Template

template = Template(open('controller_template.py').read())
output = template.render(
    resource='product',
    Resource='Product',
    resource_plural='products',
    fields=['name', 'price', 'sku']
)
```

**Handlebars (JavaScript):**
```javascript
const Handlebars = require('handlebars');
const template = Handlebars.compile(fs.readFileSync('template.ts', 'utf8'));
const output = template({
  resource: 'product',
  Resource: 'Product',
  fields: [{name: 'name', type: 'string'}, {name: 'price', type: 'number'}]
});
```

**Option 3: CLI scaffolding tools**
```bash
# NestJS generator
nest g service Product

# Django management command
python manage.py startapp products

# Rails generator
rails g scaffold Product name:string price:decimal
```

---

## Phase 5: Test Generation

### 5.1 Mirror Implementation Structure

**For every implementation file, generate companion test file:**

**Implementation:**
```
src/services/user_service.py
```

**Test:**
```
tests/unit/services/test_user_service.py
```

### 5.2 Test Template Example

**Python (pytest):**

```python
# tests/unit/services/test_{{resource}}_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.{{resource}}_service import {{Resource}}Service
from app.models.{{resource}} import {{Resource}}

@pytest.fixture
def {{resource}}_service():
    """Fixture providing {{Resource}}Service instance."""
    # TODO: Set up dependencies (database, config, etc.)
    return {{Resource}}Service()


@pytest.fixture
def sample_{{resource}}():
    """Fixture providing sample {{Resource}} for testing."""
    # TODO: Create realistic test data
    return {{Resource}}(id=1, name="Test {{Resource}}")


class Test{{Resource}}ServiceList:
    """Tests for {{Resource}}Service.list_{{resource_plural}}()"""
    
    def test_list_{{resource_plural}}_returns_all_{{resource_plural}}(self, {{resource}}_service):
        # TODO: Write test for list operation
        pytest.skip("Not implemented")
    
    def test_list_{{resource_plural}}_with_pagination(self, {{resource}}_service):
        # TODO: Write test for pagination
        pytest.skip("Not implemented")
    
    def test_list_{{resource_plural}}_empty_database(self, {{resource}}_service):
        # TODO: Write test for empty result case
        pytest.skip("Not implemented")


class Test{{Resource}}ServiceGet:
    """Tests for {{Resource}}Service.get_{{resource}}()"""
    
    def test_get_{{resource}}_by_id_returns_{{resource}}(self, {{resource}}_service, sample_{{resource}}):
        # TODO: Write test for successful get
        pytest.skip("Not implemented")
    
    def test_get_{{resource}}_not_found_raises_exception(self, {{resource}}_service):
        # TODO: Write test for not found case
        pytest.skip("Not implemented")


class Test{{Resource}}ServiceCreate:
    """Tests for {{Resource}}Service.create_{{resource}}()"""
    
    def test_create_{{resource}}_saves_to_database(self, {{resource}}_service):
        # TODO: Write test for create operation
        pytest.skip("Not implemented")
    
    def test_create_{{resource}}_validates_input(self, {{resource}}_service):
        # TODO: Write test for validation
        pytest.skip("Not implemented")
    
    def test_create_{{resource}}_duplicate_raises_exception(self, {{resource}}_service):
        # TODO: Write test for uniqueness constraint
        pytest.skip("Not implemented")


class Test{{Resource}}ServiceUpdate:
    """Tests for {{Resource}}Service.update_{{resource}}()"""
    
    def test_update_{{resource}}_modifies_existing(self, {{resource}}_service, sample_{{resource}}):
        # TODO: Write test for update operation
        pytest.skip("Not implemented")
    
    def test_update_{{resource}}_not_found_raises_exception(self, {{resource}}_service):
        # TODO: Write test for not found case
        pytest.skip("Not implemented")


class Test{{Resource}}ServiceDelete:
    """Tests for {{Resource}}Service.delete_{{resource}}()"""
    
    def test_delete_{{resource}}_removes_from_database(self, {{resource}}_service, sample_{{resource}}):
        # TODO: Write test for delete operation
        pytest.skip("Not implemented")
    
    def test_delete_{{resource}}_not_found_raises_exception(self, {{resource}}_service):
        # TODO: Write test for not found case
        pytest.skip("Not implemented")
```

**TypeScript (Jest):**

```typescript
// tests/services/{{Resource}}Service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { {{Resource}}Service } from '../../src/services/{{Resource}}Service';
import { {{Resource}} } from '../../src/entities/{{resource}}.entity';
import { Create{{Resource}}Dto, Update{{Resource}}Dto } from '../../src/dto/{{resource}}.dto';

describe('{{Resource}}Service', () => {
  let service: {{Resource}}Service;
  let repository: Repository<{{Resource}}>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        {{Resource}}Service,
        {
          provide: getRepositoryToken({{Resource}}),
          useClass: Repository,
        },
      ],
    }).compile();

    service = module.get<{{Resource}}Service>({{Resource}}Service);
    repository = module.get<Repository<{{Resource}}>>(getRepositoryToken({{Resource}}));
  });

  describe('findAll', () => {
    it('should return array of {{resource_plural}}', async () => {
      // TODO: Write test for findAll
      expect(true).toBe(false); // Placeholder - will fail until implemented
    });

    it('should respect pagination parameters', async () => {
      // TODO: Write test for pagination
      expect(true).toBe(false);
    });
  });

  describe('findOne', () => {
    it('should return {{resource}} when found', async () => {
      // TODO: Write test for successful find
      expect(true).toBe(false);
    });

    it('should throw NotFoundException when not found', async () => {
      // TODO: Write test for not found case
      expect(true).toBe(false);
    });
  });

  describe('create', () => {
    it('should create and return new {{resource}}', async () => {
      // TODO: Write test for create
      expect(true).toBe(false);
    });

    it('should validate input data', async () => {
      // TODO: Write test for validation
      expect(true).toBe(false);
    });
  });

  describe('update', () => {
    it('should update and return {{resource}}', async () => {
      // TODO: Write test for update
      expect(true).toBe(false);
    });

    it('should throw NotFoundException when {{resource}} does not exist', async () => {
      // TODO: Write test for not found case
      expect(true).toBe(false);
    });
  });

  describe('remove', () => {
    it('should delete {{resource}}', async () => {
      // TODO: Write test for delete
      expect(true).toBe(false);
    });

    it('should throw NotFoundException when {{resource}} does not exist', async () => {
      // TODO: Write test for not found case
      expect(true).toBe(false);
    });
  });
});
```

---

## Phase 6: Verification Against Conventions

### 6.1 Checklist

Before finalizing generated code, verify:

**Naming conventions:**
- [ ] File names match project convention (snake_case or PascalCase)
- [ ] Class names are PascalCase
- [ ] Method names match convention (snake_case or camelCase)
- [ ] Variable names are descriptive and follow convention

**Type safety:**
- [ ] All function parameters have type annotations
- [ ] All function return types are explicit
- [ ] No use of `any` (TypeScript) or missing hints (Python)
- [ ] Generic types are properly constrained

**Structure:**
- [ ] Imports are grouped correctly (stdlib → third-party → local)
- [ ] File is in correct directory
- [ ] Follows single responsibility principle
- [ ] Matches patterns from existing files

**Testing:**
- [ ] Test file exists alongside implementation
- [ ] Test file mirrors implementation structure
- [ ] All public methods have test stubs
- [ ] Fixtures/mocks follow project patterns

### 6.2 Automated Validation

**Run linters on generated code:**
```bash
# Python
ruff check src/controllers/product_controller.py
pyright src/controllers/product_controller.py

# TypeScript
eslint src/services/ProductService.ts
tsc --noEmit src/services/ProductService.ts
```

**Expected result:** No errors (NotImplementedError is okay, type errors are not).

---

## Phase 7: Documentation & Handoff

### 7.1 Usage Guide

Provide clear instructions for using the generated boilerplate:

**Example README section:**

```markdown
## Using Generated Boilerplate

### Files Created
- `src/controllers/product_controller.py` - Product API endpoints
- `tests/unit/controllers/test_product_controller.py` - Test suite

### Next Steps

1. **Implement business logic:**
   - Search for `# TODO:` comments (12 total)
   - Replace `raise NotImplementedError()` with actual logic
   - Remove placeholder comments when complete

2. **Fill in test cases:**
   - Search for `pytest.skip("Not implemented")` (18 total)
   - Write assertions for each test case
   - Remove skip decorators when tests are complete

3. **Update related files:**
   - Add route to `src/api/routes.py`:
     ```python
     from app.controllers.product_controller import router as product_router
     app.include_router(product_router)
     ```
   - Add model import to `src/models/__init__.py`
   - Update API documentation

### What NOT to Change

- Method signatures (breaking API contract)
- Decorator patterns (@router.get, @router.post)
- Error handling structure
- Test class organization

### Validation

Run these commands to verify implementation:
```bash
# Type checking
pyright src/controllers/product_controller.py

# Tests
pytest tests/unit/controllers/test_product_controller.py -v

# Linting
ruff check src/controllers/product_controller.py
```
```

### 7.2 Common Pitfalls

Document known issues when using generated code:

**Pitfall 1: Forgetting to register routes**
```python
# WRONG: Generated controller but forgot to register
# Result: 404 errors on all endpoints

# CORRECT: Register in app initialization
from app.controllers.product_controller import router
app.include_router(router)
```

**Pitfall 2: Implementing logic without tests**
```python
# WRONG: Implemented create_product() but didn't write tests
# Result: No coverage, bugs not caught

# CORRECT: Implement AND write tests before moving on
```

**Pitfall 3: Changing method signatures**
```python
# WRONG: Changed signature without updating callers
def create_product(self, product: ProductCreate, user_id: int):  # Added user_id
    # Result: Breaking change, existing callers fail

# CORRECT: Add new parameter with default, or create new method
def create_product(self, product: ProductCreate, user_id: Optional[int] = None):
```

---

## Best Practices

### Do:
✓ Read existing code before generating
✓ Generate structure only, not logic
✓ Include comprehensive type annotations
✓ Generate test files alongside implementation
✓ Use clear, searchable TODO comments
✓ Validate generated code with linters
✓ Provide usage documentation

### Don't:
✗ Generate business logic
✗ Use vague placeholders ("implement here")
✗ Skip type annotations
✗ Generate implementation without tests
✗ Ignore existing code patterns
✗ Use `any` or untyped parameters
✗ Leave generated code without documentation

---

## Tools & Resources

**Template engines:**
- Jinja2 (Python): jinja.palletsprojects.com
- Handlebars (JavaScript): handlebarsjs.com
- Liquid (Ruby): shopify.github.io/liquid/

**Code generators:**
- Yeoman (JavaScript): yeoman.io
- Cookiecutter (Python): cookiecutter.readthedocs.io
- Plop (Node): plopjs.com

**Framework scaffolding:**
- Rails generators: guides.rubyonrails.org/command_line.html#bin-rails-generate
- NestJS CLI: docs.nestjs.com/cli/overview
- Django management commands: docs.djangoproject.com/en/stable/howto/custom-management-commands/
