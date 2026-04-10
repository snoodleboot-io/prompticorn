---
name: "strategy-for-applications-workflow"
description: "Comprehensive strategic planning for applications with architecture decisions, tech stack selection, and scalability planning"
version: "1.0"
languages: ["python", "typescript", "architecture"]
subagents: ["architect", "orchestrator", "code"]
---

# Application Strategy Workflow (Verbose)

## Purpose
Define comprehensive strategy for building applications from concept to production. This workflow guides architecture decisions, technology selection, scalability planning, and implementation phasing.

## When to Use This Workflow
- Starting a new application from scratch
- Major rewrite or refactoring of existing application
- Migrating to new technology stack
- Scaling application to handle 10x growth
- Adding complex new capabilities to existing system

## Prerequisites
- Business requirements or product brief
- Understanding of user needs and scale expectations
- Knowledge of team capabilities
- Budget and timeline constraints
- Compliance and regulatory requirements

---

## Steps

### 1. Define Business Objectives

**Goal:** Understand the business context and success criteria.

#### 1.1 Identify the Core Problem
What problem are we solving?

**Good problem statements:**
- "Customer support team spends 40% of time answering repetitive questions"
- "Users abandon checkout due to slow payment processing (8% cart abandonment)"
- "Manual data entry causes 15% error rate in financial reports"

**Bad problem statements (too vague):**
- "We need a better website"
- "Improve customer experience"
- "Modernize our tech stack"

#### 1.2 Define Target Users
Who will use this application?

**User profile template:**
```
User Type: Customer Support Agents
Count: 50 agents
Location: Distributed (US, Europe, Asia)
Technical expertise: Low (basic computer skills)
Usage pattern: 8 hours/day, 5 days/week
Peak usage: 9am-11am EST (500 concurrent users)
```

**Scale expectations:**
- Year 1: 50 users, 10K requests/day
- Year 2: 200 users, 50K requests/day
- Year 3: 1000 users, 500K requests/day

#### 1.3 Establish Success Criteria
How do we measure success?

**Example criteria:**
```
Performance:
- Page load time <2 seconds
- API response time <200ms (p95)
- Support 1000 concurrent users

Features:
- User authentication with SSO
- Real-time notifications
- Export to Excel/PDF
- Mobile responsive

Business metrics:
- Reduce support ticket resolution time by 30%
- Increase customer satisfaction (CSAT) from 3.2 to 4.5
- Launch MVP in 3 months
```

#### 1.4 Identify Constraints
What are the limitations?

**Common constraints:**
- **Budget:** $200K for Year 1 development + infrastructure
- **Team:** 2 backend devs, 1 frontend dev, 1 DevOps engineer
- **Timeline:** MVP in 3 months, full launch in 6 months
- **Compliance:** GDPR, SOC 2 Type II required
- **Integration:** Must integrate with Salesforce, Slack, Zendesk
- **Technology:** Must use company-approved cloud provider (AWS)

---

### 2. Analyze Requirements

**Goal:** Break down functional and non-functional requirements.

#### 2.1 Functional Requirements
What features does the application need?

**Feature prioritization (MoSCoW):**

**Must Have (MVP):**
- User authentication (email/password)
- View knowledge base articles
- Search articles by keyword
- Submit support ticket
- Admin panel to manage articles

**Should Have (Phase 2):**
- SSO integration (Okta)
- Real-time chat support
- File attachments to tickets
- Analytics dashboard

**Could Have (Phase 3):**
- AI-powered article suggestions
- Video tutorials
- Multi-language support

**Won't Have (Out of Scope):**
- Mobile native apps (web responsive only)
- Integration with legacy CRM
- Custom branding per customer

#### 2.2 Non-Functional Requirements (NFRs)

**Performance:**
```
Response time:
- API endpoints: <200ms (p95), <500ms (p99)
- Page load: <2s (p95)
- Search results: <500ms

Throughput:
- 1000 concurrent users
- 10K requests/minute peak

Availability:
- 99.9% uptime (43 min downtime/month allowed)
- RTO (Recovery Time Objective): <1 hour
- RPO (Recovery Point Objective): <15 minutes
```

**Security:**
```
- Authentication: OAuth 2.0 + JWT
- Authorization: Role-based access control (RBAC)
- Data encryption: TLS 1.3 in transit, AES-256 at rest
- Password policy: Min 12 chars, complexity requirements
- Session timeout: 30 min idle, 24 hours max
- Audit logging: All data access logged
```

**Scalability:**
```
- Horizontal scaling: Support adding servers without downtime
- Database: Read replicas for read-heavy workloads
- Caching: Redis for session data and frequently accessed content
- CDN: Static assets served via CloudFront
```

**Reliability:**
```
- Error rate: <0.1% (99.9% success rate)
- Data durability: 99.999999999% (11 nines)
- Automated backups: Every 6 hours, retained 30 days
- Health checks: Every 30 seconds
```

#### 2.3 Integration Requirements
What external systems must we integrate with?

**Integration matrix:**

| System | Purpose | Method | Frequency | Criticality |
|--------|---------|--------|-----------|-------------|
| Salesforce | Sync customer data | REST API | Real-time | High |
| Slack | Notifications | Webhooks | Event-driven | Medium |
| Zendesk | Ticket sync | REST API | Every 5 min | High |
| Okta | SSO auth | SAML 2.0 | Per login | High |
| Stripe | Payment processing | REST API | Per transaction | High |

#### 2.4 Compliance Requirements
What regulations apply?

**GDPR (for EU users):**
- Right to access: Users can download their data
- Right to erasure: Users can request deletion
- Data portability: Export data in machine-readable format
- Consent management: Explicit opt-in for data processing
- Data breach notification: Within 72 hours

**SOC 2 Type II:**
- Access controls: MFA for all admin access
- Audit logging: All data access logged and retained 1 year
- Encryption: Data encrypted at rest and in transit
- Change management: All changes tracked and approved
- Incident response: Documented procedure, tested quarterly

---

### 3. Design System Architecture

**Goal:** Define the system's structure and components.

#### 3.1 Choose Architecture Pattern

**Monolith vs Microservices vs Serverless:**

**Monolith (recommended for MVP):**
```
Pros:
- Simple deployment (single artifact)
- Easy local development
- Faster initial development
- Easier debugging
- Lower infrastructure cost

Cons:
- Harder to scale specific components
- Longer deployment times as app grows
- Technology lock-in (one language/framework)

When to use:
- MVP or new product (unproven scale)
- Small team (<10 developers)
- Simple domain with few bounded contexts
```

**Microservices:**
```
Pros:
- Independent scaling per service
- Technology flexibility
- Team autonomy
- Fault isolation

Cons:
- Complex infrastructure
- Distributed system challenges
- Higher operational overhead
- Slower initial development

When to use:
- Proven product with clear bounded contexts
- Large team (>20 developers)
- Different scaling needs per component
- Need for technology diversity
```

**Serverless:**
```
Pros:
- Auto-scaling
- Pay per use
- No server management
- Fast time to market

Cons:
- Vendor lock-in
- Cold start latency
- Complex debugging
- Cost unpredictability at scale

When to use:
- Event-driven workloads
- Bursty traffic
- Small team, want low ops overhead
- Prototype or side project
```

**Decision for our example (Support Portal):**
```
Choice: Monolith (for MVP)
Rationale:
- Small team (3 devs)
- Unproven scale (starting with 50 users)
- Simple domain (CRUD + search)
- 3-month timeline (microservices too complex)
- Can refactor to microservices later if needed
```

#### 3.2 Define Component Architecture

**High-level architecture:**
```
┌─────────────────┐
│  Web Browser    │
│  (React SPA)    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Load Balancer  │
│  (ALB)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Server     │
│  (FastAPI)      │
│  - Auth         │
│  - Articles     │
│  - Tickets      │
│  - Search       │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Postgres│ │ Redis  │ │Elasticsearch│
│ (data)  │ │(cache) │ │  (search) │
└─────────┘ └────────┘ └─────────┘
```

**Component responsibilities:**

**Frontend (React):**
- User interface rendering
- Client-side routing
- Form validation
- API communication
- State management (Redux)

**Backend (FastAPI):**
- REST API endpoints
- Business logic
- Authentication/authorization
- Database operations
- Integration with external services

**Database (PostgreSQL):**
- User accounts
- Articles content
- Support tickets
- Audit logs

**Cache (Redis):**
- Session data
- Frequently accessed articles
- Search result caching
- Rate limiting counters

**Search (Elasticsearch):**
- Full-text article search
- Autocomplete suggestions
- Analytics aggregations

#### 3.3 Design Data Model

**Core entities:**

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'admin', 'agent', 'user'
    created_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);

-- Articles
CREATE TABLE articles (
    id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    author_id UUID REFERENCES users(id),
    category VARCHAR(100),
    view_count INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Support Tickets
CREATE TABLE tickets (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    subject VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'open', 'in_progress', 'resolved'
    priority VARCHAR(50), -- 'low', 'medium', 'high', 'urgent'
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_published ON articles(published_at);
CREATE INDEX idx_tickets_user ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assigned ON tickets(assigned_to);
```

#### 3.4 Plan for Scalability

**Horizontal scaling strategy:**

```
Phase 1 (0-1K users):
- Single application server
- Single database instance
- No caching layer needed

Phase 2 (1K-10K users):
- 2-3 application servers behind load balancer
- Database read replica for reports/analytics
- Redis cache for sessions and hot data

Phase 3 (10K-100K users):
- Auto-scaling group (5-20 servers)
- Database sharding by customer ID
- CDN for static assets
- Elasticsearch cluster (3 nodes)
- Redis cluster (3 nodes)
```

**Caching strategy:**
```
Layer 1: CDN (CloudFront)
- Static assets (JS, CSS, images)
- TTL: 7 days

Layer 2: Redis (application cache)
- Article content (popular articles)
- Search results (recent queries)
- Session data
- TTL: 5 minutes to 1 hour

Layer 3: Database query cache
- PostgreSQL query result cache
- TTL: Managed by database
```

---

### 4. Select Technology Stack

**Goal:** Choose technologies that fit requirements and team capabilities.

#### 4.1 Backend Framework Selection

**Options considered:**

| Framework | Language | Pros | Cons | Score |
|-----------|----------|------|------|-------|
| **FastAPI** | Python | Fast, async, auto docs, modern | Smaller ecosystem than Django | 9/10 |
| Django | Python | Mature, batteries included, ORM | Slower, sync-first | 7/10 |
| Express | Node.js | Simple, flexible, huge ecosystem | No structure, manual setup | 6/10 |
| Spring Boot | Java | Enterprise-ready, robust | Verbose, heavy | 5/10 |

**Decision: FastAPI**
- Team knows Python
- Async support for high concurrency
- Auto-generated API docs (OpenAPI)
- Fast development with type hints
- Good performance

#### 4.2 Frontend Framework Selection

| Framework | Pros | Cons | Score |
|-----------|------|------|-------|
| **React** | Huge ecosystem, flexible, jobs market | Need additional libraries | 9/10 |
| Vue | Easier learning curve, good docs | Smaller ecosystem | 7/10 |
| Angular | Full framework, TypeScript first | Heavy, steep learning curve | 6/10 |
| Svelte | Fast, less boilerplate | Small ecosystem, fewer jobs | 6/10 |

**Decision: React**
- Team has React experience
- Large ecosystem (libraries for everything)
- Good hiring market
- Mature tooling (Create React App, Next.js option)

#### 4.3 Database Selection

| Database | Type | Pros | Cons | Score |
|----------|------|------|------|-------|
| **PostgreSQL** | Relational | ACID, reliable, full-text search, JSON support | Scaling requires sharding | 9/10 |
| MongoDB | Document | Flexible schema, horizontal scaling | No ACID (unless replica set), eventual consistency | 6/10 |
| MySQL | Relational | Widely used, familiar | Less features than Postgres | 7/10 |

**Decision: PostgreSQL**
- Strong ACID guarantees (important for tickets, user data)
- Full-text search built-in (simple searches without Elasticsearch)
- JSON support for flexible fields
- Team familiarity

#### 4.4 Infrastructure Selection

**Cloud Provider: AWS**
- Company standard
- Team familiarity
- Comprehensive services

**Services used:**
```
Compute: ECS (Fargate) for containers
Load Balancer: Application Load Balancer (ALB)
Database: RDS PostgreSQL (Multi-AZ for HA)
Cache: ElastiCache (Redis)
Search: Managed Elasticsearch
Storage: S3 for file uploads
CDN: CloudFront
Monitoring: CloudWatch + DataDog
CI/CD: GitHub Actions + AWS CodeDeploy
```

---

### 5. Plan Implementation Approach

**Goal:** Break work into phases with clear deliverables.

#### 5.1 Define MVP Scope (Phase 1: Months 1-3)

**Must-have features:**
1. User authentication (email/password)
2. Article management (CRUD)
3. Article search (basic keyword)
4. Submit support ticket
5. View ticket status
6. Admin panel for agents

**Success criteria:**
- 50 users can use the system
- <2s page load time
- <200ms API response time
- 99% uptime

**Deliverables:**
- Deployed application on AWS
- Basic documentation
- Admin training materials

#### 5.2 Phase 2: Scale and Enhance (Months 4-6)

**Features:**
1. SSO integration (Okta)
2. Real-time notifications (WebSockets)
3. File attachments to tickets
4. Advanced search (filters, facets)
5. Analytics dashboard
6. Salesforce integration

**Success criteria:**
- 200 users supported
- SSO working
- Real-time updates <1s delay

#### 5.3 Phase 3: Advanced Features (Months 7-12)

**Features:**
1. AI-powered article suggestions
2. Ticket auto-routing
3. Chat widget for websites
4. Mobile app (React Native)
5. Multi-language support

#### 5.4 Estimate Timeline and Resources

**Phase 1 (MVP) - 12 weeks:**
```
Week 1-2: Setup & Architecture
- AWS infrastructure setup (DevOps)
- Database schema design (Backend)
- React app scaffolding (Frontend)

Week 3-5: Core Features
- Auth system (Backend: 1 week)
- Article CRUD (Backend: 1 week, Frontend: 1 week)
- Basic search (Backend: 3 days, Frontend: 2 days)

Week 6-8: Support Tickets
- Ticket creation (Backend: 1 week, Frontend: 3 days)
- Ticket management (Backend: 4 days, Frontend: 1 week)

Week 9-10: Admin Panel
- User management (1 week)
- Article moderation (1 week)

Week 11: Testing & Bug Fixes
- Integration testing
- Load testing
- Bug fixes

Week 12: Deployment & Launch
- Production deployment
- User training
- Monitoring setup
```

**Resource allocation:**
- 2 backend devs × 12 weeks = 24 dev-weeks
- 1 frontend dev × 12 weeks = 12 dev-weeks
- 1 DevOps × 4 weeks (partial) = 4 dev-weeks
- Total: 40 dev-weeks

#### 5.5 Identify Risks and Mitigation

**Risk register:**

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Database performance degrades at scale | Medium | High | Implement caching early, load test with realistic data |
| SSO integration complex | High | Medium | Start Okta integration in week 8 (before Phase 2) |
| Search quality poor | Medium | High | Prototype Elasticsearch in week 4, can fallback to Postgres |
| Team member leaves | Low | High | Document architecture, pair programming |
| AWS costs exceed budget | Medium | Medium | Set billing alarms, use reserved instances |

---

### 6. Validate Strategy

**Goal:** Confirm strategy is sound before committing resources.

#### 6.1 Review with Stakeholders
Present strategy to:
- Engineering leadership
- Product manager
- Finance (budget approval)
- Security team (compliance review)
- Operations team (support readiness)

**Stakeholder feedback template:**
```
Presented to: VP Engineering, Product Manager
Date: 2026-04-15
Feedback:
- Concern: Can we really build this in 3 months?
- Response: Reduced MVP scope, moved SSO to Phase 2
- Approval: Approved with revised timeline
```

#### 6.2 Prototype Critical Components
Build spikes for risky/unknown areas:

**Spike 1: Elasticsearch integration**
- Goal: Verify search quality with sample data
- Time: 2 days
- Outcome: Search results acceptable, proceed

**Spike 2: Real-time notifications**
- Goal: Test WebSocket scalability (1000 concurrent connections)
- Time: 1 day
- Outcome: Socket.io handles load, proceed

**Spike 3: Salesforce API integration**
- Goal: Test data sync reliability
- Time: 3 days
- Outcome: API rate limits stricter than expected, need caching

#### 6.3 Validate Assumptions
Test key assumptions:

**Assumption 1: PostgreSQL full-text search is good enough for MVP**
- Test: Index 10K articles, search with common queries
- Result: <100ms response time, relevance acceptable ✓

**Assumption 2: Fargate costs are within budget**
- Calculation: 2 tasks × 0.5 vCPU × 1GB × $0.04/hour × 730 hours = $29/month
- Result: Under $200/month infrastructure budget ✓

**Assumption 3: Team can deliver in 12 weeks**
- Review: Compared to past projects of similar scope
- Result: Realistic with reduced MVP scope ✓

#### 6.4 Get Approval and Commit
Final checklist before starting:

```
Strategy Approval Checklist:
- [ ] Business objectives documented
- [ ] Requirements validated with product team
- [ ] Architecture reviewed by senior engineers
- [ ] Technology stack approved by engineering leadership
- [ ] Budget approved by finance
- [ ] Compliance requirements reviewed by security
- [ ] Timeline committed by team
- [ ] Risks identified and mitigation planned
- [ ] All stakeholders signed off

Status: APPROVED - Proceed with implementation
```

---

## Complete Example: Building a SaaS Analytics Platform

**Business Objective:**
Build a web analytics platform for small businesses (competitor to Google Analytics but simpler).

**Users:**
- Year 1: 100 businesses (10K events/day)
- Year 3: 10K businesses (100M events/day)

**Success Criteria:**
- <50ms event ingestion
- Real-time dashboard updates
- $10/month pricing (must be profitable)

**Architecture Decision:**
```
Monolith rejected: Need to scale ingestion independently from dashboard
Microservices rejected: Too complex for small team
Serverless chosen: Auto-scaling, pay-per-use aligns with business model

Components:
- Event ingestion: AWS Lambda (handles spikes)
- Storage: DynamoDB (scalable, low latency)
- Analytics: Athena (query historical data)
- Dashboard: React + API Gateway + Lambda
```

**Tech Stack:**
- Backend: Python Lambda functions
- Frontend: React (hosted on S3 + CloudFront)
- Database: DynamoDB (events), RDS (customer data)
- Queue: SQS (event buffer)
- Analytics: Athena + S3 (data lake)

**Implementation Plan:**
```
Phase 1 (MVP): Event tracking + basic dashboard (8 weeks)
Phase 2: Advanced analytics (4 weeks)
Phase 3: Custom reports (4 weeks)
```

**Cost validation:**
```
Lambda: $0.20 per 1M requests
DynamoDB: $1.25/GB/month
S3: $0.023/GB/month
Estimated cost for 10K businesses: $500/month
Revenue: 10K × $10 = $100K/month
Margin: 99.5% ✓ Profitable
```

**Result:** Strategy approved, launched successfully in 4 months.
