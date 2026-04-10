---
name: test-aaa-structure
description: Apply Arrange-Act-Assert pattern for clear tests
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
tools_needed: [read, write]
---

## Instructions

Structure tests using **Arrange-Act-Assert** (AAA):

1. **Arrange:** Set up state and inputs
2. **Act:** Call the function/method under test
3. **Assert:** Verify outputs and side effects

### Key Rules

- One logical assertion per test
- Descriptive test names (read like sentences)
- Separate AAA sections with blank lines or comments

### Example

```python
def test_get_user_returns_user_when_found():
    # Arrange
    user = User(id="123", name="Alice")
    db.save(user)
    
    # Act
    result = get_user_by_id("123")
    
    # Assert
    assert result.name == "Alice"
```


