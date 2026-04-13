---
name: multi-agent-coordination
description: Coordinate multiple agents working together on shared tasks with clear communication and state management
type: workflow
category: workflow-patterns
minimal: true
---

# Multi-Agent Coordination Workflow

## Agent Roles
- **Coordinator:** Manages task distribution and state
- **Workers:** Execute assigned tasks
- **Aggregator:** Collects and merges results

## Coordination Mechanisms
- **Message Queue:** Tasks and results flow through queue
- **Shared State:** Central state accessible to all agents
- **Consensus:** Agents agree on decisions

## Communication Patterns
- **Request-Response:** Agent asks coordinator for work
- **Publish-Subscribe:** Agents watch state for changes
- **Broadcast:** Coordinator notifies all agents

## Synchronization
- Barriers: Wait for all agents to reach checkpoint
- Locks: Protect shared resources
- Atomic Operations: Prevent race conditions
