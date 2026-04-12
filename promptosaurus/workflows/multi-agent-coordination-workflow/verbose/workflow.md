---
name: multi-agent-coordination-workflow
description: Coordinate multiple agents working together on shared tasks with clear communication and state management
type: workflow
category: workflow-patterns
minimal: false
---

# Multi-Agent Coordination Workflow

## 1. Coordinator Pattern

One agent coordinates, others execute tasks.

### Architecture:
```
Coordinator Agent
    ↓ (distributes tasks)
Worker 1  Worker 2  Worker 3
    ↓         ↓         ↓
  Result   Result    Result
    ↓ (aggregates)
  Final Output
```

### Implementation:
```yaml
agents:
  coordinator:
    role: task_distribution
    responsibilities:
      - queue_management
      - result_collection
      - state_tracking
  
  worker:
    role: task_execution
    responsibilities:
      - request_task
      - execute
      - report_result
```

### Use Cases:
- Map-reduce operations
- Distributed data processing
- Parallel testing

---

## 2. Peer-to-Peer Coordination

Agents negotiate directly with each other.

### Characteristics:
- No central coordinator
- Agents can initiate tasks
- Decentralized decision-making
- Requires consensus

### Communication:
```
Agent A ↔ Agent B
  ↓       ↓
Agent C ↔ Agent D
```

### Use Cases:
- Distributed consensus
- Collaborative planning
- Decentralized systems

---

## 3. State-Based Coordination

Shared mutable state drives agent actions.

### State Structure:
```yaml
workflow_state:
  tasks:
    - id: task_1
      status: pending
      assigned_to: null
  agents:
    - id: agent_1
      status: idle
  results: {}
```

### Flow:
1. Agent reads state
2. Claims available task
3. Executes task
4. Updates state with result

---

## 4. Message Queue Coordination

Tasks and results flow through message queue.

### Implementation:
```
Producer → Queue → Consumer
Coordinator → Tasks Queue → Workers
Workers → Results Queue → Aggregator
```

### Benefits:
- Decouples agent lifetimes
- Handles load spikes
- Natural backpressure
- Retryable messages

---

## 5. Consensus and Voting

Multiple agents decide together.

### Mechanisms:
- **Majority Vote:** Threshold-based approval
- **Quorum:** Minimum participants required
- **Byzantine Fault Tolerance:** Tolerate faulty agents

### Use Cases:
- Approval workflows
- Group decisions
- Fault-tolerant systems

---

## Communication Patterns

### Request-Response
```
Worker → Coordinator: "Give me work"
Coordinator → Worker: "Here's task X"
Worker → Coordinator: "Task X done, result Y"
```

### Publish-Subscribe
```
Coordinator publishes: "Task queue updated"
Workers subscribe and react
Results published on completion
```

### Broadcast
```
Coordinator → All Workers: "Workflow cancelled"
Workers acknowledge and cleanup
```

---

## Synchronization Mechanisms

### Barriers
Wait for all agents to reach checkpoint.

```yaml
barrier:
  name: all_agents_ready
  participants: [agent_1, agent_2, agent_3]
  timeout: 30s
  on_timeout: cancel_workflow
```

### Locks
Protect shared resources from concurrent access.

```yaml
lock:
  resource: shared_cache
  owner: agent_1
  duration: 5s
```

### Atomic Operations
Execute without interruption.

```yaml
atomic:
  - read_value
  - increment
  - write_value
```

---

## Error Handling

### Agent Failure
- Detect: Heartbeat timeout
- Handle: Reassign task to another agent
- Retry: Up to N times

### Deadlock Detection
- Cycle detection in dependencies
- Timeout-based recovery

### Partial Failures
- Some agents succeed, some fail
- Determine if overall success or rollback

---

## Best Practices

1. **Idempotency:** Tasks safe to execute multiple times
2. **Timeouts:** Always set timeouts on waits
3. **Health Checks:** Monitor agent availability
4. **Logging:** Trace all coordination decisions
5. **Testing:** Test agent failures and recovery
6. **Scaling:** Design for adding/removing agents
