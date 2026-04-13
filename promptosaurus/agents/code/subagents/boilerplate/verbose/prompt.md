---
name: code-boilerplate-verbose
version: 1.0.0
description: Detailed boilerplate generation with examples and templates
mode: subagent
tags: [code, boilerplate, verbose]
tools: [read]
---

# Code Boilerplate (Verbose)

Complete guide to generating structural code scaffolding without implementing business logic.

## Philosophy

Boilerplate generation is about creating **structure and contracts**, not implementation. The goal is to establish type-safe interfaces that guide implementation while leaving logic as TODO items.

## Complete Workflow

### Step 1: Pattern Discovery

Before generating any code, understand existing patterns:

```bash
# Find similar files
find src -name "*service*.py" | head -3
find src -name "*repository*.ts" | head -3

# Read patterns
cat src/services/user_service.py
cat src/repositories/order_repository.ts
```

**What to extract:**
- Import organization (stdlib → third-party → local)
- Class structure (inheritance, mixins, interfaces)
- Method naming conventions
- Error handling patterns
- Logging patterns
- Decorator usage

### Step 2: Gather Requirements

Ask these questions if not provided:

1. **Type**: What are we generating?
   - React component
   - API endpoint/route
   - Service class
   - Repository/DAO
   - Model/entity
   - Custom hook
   - Middleware
   - CLI command

2. **Name**: What should it be called?
   - Must follow Core Conventions naming
   - PascalCase for classes/components
   - snake_case for files (Python)
   - kebab-case for files (TypeScript)

3. **Purpose**: What does it do? (one sentence)

4. **Dependencies**: What does it depend on?
   - Database access?
   - External APIs?
   - Other services?

### Step 3: Generate Structure

#### Python Service Example

```python
# src/services/notification_service.py
from typing import Protocol
from src.models.user import User
from src.models.notification import Notification
import logging

logger = logging.getLogger(__name__)

class NotificationProvider(Protocol):
    """Interface for notification providers."""
    def send(self, recipient: str, message: str) -> bool:
        ...

class NotificationService:
    """Service for sending notifications to users.
    
    Handles notification delivery via multiple channels (email, SMS, push).
    Logs all notification attempts and tracks delivery status.
    """
    
    def __init__(self, provider: NotificationProvider) -> None:
        """Initialize notification service.
        
        Args:
            provider: Notification delivery provider
        """
        self._provider = provider
        self._logger = logger
    
    def send_to_user(self, user: User, message: str) -> bool:
        """Send notification to specific user.
        
        Args:
            user: Target user for notification
            message: Notification message content
            
        Returns:
            True if notification sent successfully, False otherwise
            
        Raises:
            ValueError: If user has no notification preferences set
        """
        # TODO: implement
        # 1. Check user notification preferences
        # 2. Validate message content
        # 3. Call provider.send()
        # 4. Log delivery attempt
        # 5. Return result
        raise NotImplementedError("send_to_user not yet implemented")
    
    def send_bulk(self, users: list[User], message: str) -> dict[str, bool]:
        """Send notification to multiple users.
        
        Args:
            users: List of target users
            message: Notification message content
            
        Returns:
            Dict mapping user ID to delivery status
        """
        # TODO: implement
        # 1. Validate input
        # 2. For each user, call send_to_user()
        # 3. Collect results
        # 4. Return status map
        raise NotImplementedError("send_bulk not yet implemented")
```

#### TypeScript API Route Example

```typescript
// src/routes/webhooks.ts
import { Router, Request, Response, NextFunction } from 'express';
import { WebhookService } from '@/services/webhook-service';
import { AuthMiddleware } from '@/middleware/auth';
import { z } from 'zod';

const router = Router();

// Request validation schemas
const CreateWebhookSchema = z.object({
  url: z.string().url(),
  events: z.array(z.enum(['user.created', 'user.updated', 'user.deleted'])),
  secret: z.string().min(16).optional(),
});

type CreateWebhookRequest = z.infer<typeof CreateWebhookSchema>;

/**
 * POST /webhooks
 * Create a new webhook subscription
 */
router.post(
  '/webhooks',
  AuthMiddleware.requireAuth,
  async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // TODO: implement
      // 1. Validate request body against CreateWebhookSchema
      // 2. Extract user ID from auth context
      // 3. Call WebhookService.create()
      // 4. Return 201 with created webhook
      // 5. Handle validation errors → 400
      // 6. Handle service errors → 500
      
      res.status(501).json({ error: 'Not implemented' });
    } catch (error) {
      next(error);
    }
  }
);

/**
 * GET /webhooks
 * List user's webhook subscriptions
 */
router.get(
  '/webhooks',
  AuthMiddleware.requireAuth,
  async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      // TODO: implement
      // 1. Extract user ID from auth context
      // 2. Call WebhookService.listByUser()
      // 3. Return 200 with webhook list
      // 4. Handle service errors → 500
      
      res.status(501).json({ error: 'Not implemented' });
    } catch (error) {
      next(error);
    }
  }
);

export default router;
```

#### React Component Example

```typescript
// src/components/UserProfileCard.tsx
import React, { useState, useEffect } from 'react';
import { User } from '@/types/user';

interface UserProfileCardProps {
  userId: string;
  onEdit?: (user: User) => void;
  showActions?: boolean;
}

/**
 * Displays user profile information in a card layout.
 */
export const UserProfileCard: React.FC<UserProfileCardProps> = ({
  userId,
  onEdit,
  showActions = false,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // TODO: implement
    // 1. Fetch user data by userId
    // 2. Set loading state
    // 3. Handle success → setUser()
    // 4. Handle error → setError()
  }, [userId]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <div>User not found</div>;
  }

  return (
    <div className="user-profile-card">
      {/* TODO: implement UI */}
      <p>UserProfileCard component (not implemented)</p>
    </div>
  );
};
```

### Step 4: Generate Test Skeleton

Always generate test file alongside implementation:

```python
# tests/unit/services/test_notification_service.py
import pytest
from src.services.notification_service import NotificationService
from src.models.user import User

class MockNotificationProvider:
    """Mock notification provider for testing."""
    
    def __init__(self):
        self.sent_messages: list[tuple[str, str]] = []
    
    def send(self, recipient: str, message: str) -> bool:
        self.sent_messages.append((recipient, message))
        return True

@pytest.fixture
def service(mock_provider):
    return NotificationService(provider=mock_provider)

class TestNotificationService:
    """Test suite for NotificationService."""
    
    def test_send_to_user_sends_notification(self, service):
        # TODO: implement test
        pytest.skip("Test not implemented")
    
    def test_send_bulk_handles_multiple_users(self, service):
        # TODO: implement test
        pytest.skip("Test not implemented")
```

## Parameterization Templates

### Service Class Template

```python
from typing import Protocol
import logging

logger = logging.getLogger(__name__)

class {InterfaceName}(Protocol):
    """Interface for {description}."""
    def {method_name}(self, {params}) -> {return_type}:
        ...

class {ClassName}:
    """Service for {purpose}."""
    
    def __init__(self, {dependencies}) -> None:
        """Initialize {class_name}."""
        self._logger = logger
    
    def {public_method}(self, {params}) -> {return_type}:
        """Docstring."""
        # TODO: implement
        raise NotImplementedError()
```

## What NOT to Implement

### ❌ Never Generate These Without Asking:

1. **Business Logic**
   ```python
   # Don't do this:
   def calculate_price(self, item: Item) -> Decimal:
       base_price = item.price
       if item.category == "electronics":
           tax = base_price * Decimal("0.08")
       return base_price + tax
   
   # Instead:
   def calculate_price(self, item: Item) -> Decimal:
       """Calculate final price including taxes."""
       # TODO: implement tax calculation logic
       raise NotImplementedError()
   ```

2. **Database Queries**
   ```python
   # Don't do this:
   def get_user(self, user_id: str) -> User | None:
       result = session.query(User).filter(User.id == user_id).first()
       return result
   
   # Instead:
   def get_user(self, user_id: str) -> User | None:
       """Retrieve user by ID."""
       # TODO: implement database query
       raise NotImplementedError()
   ```

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Implementing Logic

**Wrong:**
```python
class UserService:
    def create_user(self, email: str, password: str) -> User:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(email=email, password=hashed_password)
        session.add(user)
        session.commit()
        return user
```

**Correct:**
```python
class UserService:
    def create_user(self, email: str, password: str) -> User:
        """Create new user account.
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
        """
        # TODO: implement
        # 1. Validate email format
        # 2. Check if email already exists
        # 3. Hash password using bcrypt
        # 4. Create User object
        # 5. Save to database
        # 6. Return created user
        raise NotImplementedError()
```

## Checklist Before Delivery

```markdown
- [ ] Read 1-2 existing files from same layer
- [ ] Matched import style from existing code
- [ ] All public methods have type annotations
- [ ] All public methods have docstrings
- [ ] No business logic implemented
- [ ] TODO comments explain what to implement
- [ ] Test file skeleton created
- [ ] No `any` or `unknown` types without justification
```
