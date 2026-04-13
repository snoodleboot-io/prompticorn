---
name: analytics-setup
description: "Implementation guide for product analytics and measurement"
agent: "product"
category: "product"
related_workflows:
  - a-b-testing-workflow
  - feature-launch-checklist
---

# Analytics Setup Workflow - Comprehensive Guide

## Overview

Analytics setup is the systematic process of implementing comprehensive measurement systems to track product performance, user behavior, and business outcomes. This workflow provides a structured approach to designing, implementing, and maintaining analytics infrastructure that enables data-driven decision making. Effective analytics setup transforms raw data into actionable insights that drive product success.

## Prerequisites

### Team and Stakeholders
- Product managers/analysts
- Data engineers
- Frontend/backend developers
- Marketing team
- Business intelligence team
- Legal/compliance (for privacy)
- Executive stakeholders

### Tools and Platforms
- Analytics platforms (Google Analytics, Mixpanel, Amplitude, Segment)
- Tag management (Google Tag Manager, Tealium)
- Data warehouses (BigQuery, Snowflake, Redshift)
- Visualization tools (Looker, Tableau, Power BI)
- Session recording (Hotjar, FullStory)
- Error tracking (Sentry, Rollbar)

### Required Preparations
- Business objectives defined
- Key metrics identified
- Privacy policy updated
- Technical infrastructure ready
- Budget allocated
- Team training planned

## Step-by-Step Process

### Phase 1: Strategy and Planning

#### Step 1: Define Measurement Strategy
**Key Questions:**
- What business outcomes are we driving?
- Which user behaviors indicate success?
- What decisions will data inform?
- How will we act on insights?
- What's our data governance policy?

**Measurement Framework:**
```
Business Objective: Increase user engagement
Key Metric: Weekly Active Users (WAU)
Supporting Metrics:
  - Session frequency
  - Feature adoption
  - Time in app
  - Actions per session
Segments:
  - New vs returning
  - Free vs paid
  - Mobile vs desktop
```

#### Step 2: Identify Key Metrics
**North Star Metric:**
- Single metric reflecting core value
- Leading indicator of success
- Actionable by teams
- Simple to understand

Examples:
- **SaaS:** Monthly Active Users
- **E-commerce:** GMV (Gross Merchandise Value)
- **Marketplace:** Transactions completed
- **Content:** Time spent engaging

**AARRR Framework (Pirate Metrics):**
```
Acquisition: How do users find us?
  - Traffic sources
  - Cost per acquisition
  - Channel effectiveness

Activation: Do users have a great first experience?
  - Signup completion
  - Onboarding completion
  - First action taken

Retention: Do users come back?
  - DAU/MAU ratio
  - Cohort retention
  - Churn rate

Revenue: How do we make money?
  - ARPU (Average Revenue Per User)
  - LTV (Lifetime Value)
  - Conversion rate

Referral: Do users tell others?
  - Viral coefficient
  - NPS score
  - Referral rate
```

#### Step 3: Design Data Architecture
**Data Layers:**

**Collection Layer:**
- Client-side tracking (JavaScript SDK)
- Server-side tracking (API calls)
- Mobile SDK integration
- Third-party integrations

**Processing Layer:**
- Event validation
- Data enrichment
- Identity resolution
- Session stitching

**Storage Layer:**
- Real-time database
- Data warehouse
- Data lake
- Archive storage

**Analysis Layer:**
- BI tools
- Custom dashboards
- ML models
- Reporting automation

### Phase 2: Implementation Planning

#### Step 4: Create Tracking Plan
**Event Taxonomy:**
```
Naming Convention: [object]_[action]
Examples:
  - user_signed_up
  - video_played
  - item_added_to_cart
  - payment_completed
  
Properties Convention: snake_case
Examples:
  - user_id
  - session_id
  - item_price
  - video_duration_seconds
```

**Event Schema:**
```json
{
  "event_name": "item_viewed",
  "event_timestamp": "2024-03-15T10:30:00Z",
  "user_properties": {
    "user_id": "user_123",
    "user_type": "premium",
    "signup_date": "2024-01-01"
  },
  "event_properties": {
    "item_id": "prod_456",
    "item_name": "Blue Widget",
    "item_category": "widgets",
    "item_price": 29.99,
    "currency": "USD"
  },
  "context_properties": {
    "platform": "web",
    "device_type": "mobile",
    "browser": "Chrome",
    "utm_source": "google",
    "utm_campaign": "spring_sale"
  }
}
```

#### Step 5: Define User Properties
**User Identification:**
- Anonymous ID (before login)
- User ID (after login)
- Identity linking strategy
- Cross-device tracking

**User Attributes:**
```
Demographic:
  - age_range
  - country
  - language
  
Behavioral:
  - user_type (free/paid)
  - subscription_tier
  - lifetime_value
  - last_active_date
  
Acquisition:
  - signup_date
  - acquisition_source
  - first_utm_source
  - referral_code
```

#### Step 6: Plan Implementation Phases
**Phase 1: Foundation (Week 1-2)**
- Basic tracking setup
- User identification
- Core events
- Basic dashboards

**Phase 2: Enhancement (Week 3-4)**
- Advanced events
- Custom properties
- Segmentation
- Funnel tracking

**Phase 3: Optimization (Week 5-6)**
- A/B testing setup
- Attribution modeling
- Predictive analytics
- Advanced dashboards

### Phase 3: Technical Implementation

#### Step 7: Install Analytics SDKs
**Web Implementation:**
```javascript
// Initialize analytics
analytics.initialize('YOUR_API_KEY', {
  trackingOptions: {
    ip: false,  // Privacy compliance
    deviceId: true,
    sessionId: true
  }
});

// Track page views
analytics.page('Home Page', {
  title: 'Welcome to Our Site',
  url: window.location.href,
  referrer: document.referrer
});

// Track events
analytics.track('Button Clicked', {
  button_name: 'Sign Up',
  button_location: 'header',
  variant: 'blue_cta'
});

// Identify users
analytics.identify('user_123', {
  email: 'user@example.com',
  plan: 'premium',
  created_at: '2024-01-01'
});
```

**Mobile Implementation:**
```swift
// iOS Example
Analytics.shared.track("Item Viewed", properties: [
  "item_id": "prod_123",
  "item_name": "Premium Feature",
  "item_price": 9.99
])
```

#### Step 8: Implement Data Layer
**Google Tag Manager Data Layer:**
```javascript
window.dataLayer = window.dataLayer || [];

// E-commerce example
dataLayer.push({
  'event': 'purchase',
  'ecommerce': {
    'purchase': {
      'actionField': {
        'id': 'T12345',
        'revenue': '35.43',
        'tax': '4.90',
        'shipping': '5.99'
      },
      'products': [{
        'name': 'Product Name',
        'id': 'SKU123',
        'price': '15.25',
        'brand': 'Brand Name',
        'category': 'Category',
        'quantity': 2
      }]
    }
  }
});
```

#### Step 9: Configure User Identification
**Identity Resolution:**
```javascript
// Link anonymous to known user
function onUserLogin(userId, userEmail) {
  // Get anonymous ID
  const anonymousId = analytics.getAnonymousId();
  
  // Identify user
  analytics.identify(userId, {
    email: userEmail,
    anonymous_id: anonymousId
  });
  
  // Track login event
  analytics.track('User Logged In', {
    login_method: 'email',
    previous_anonymous_id: anonymousId
  });
}
```

### Phase 4: Dashboard and Reporting

#### Step 10: Create Dashboards
**Executive Dashboard:**
- Business metrics overview
- Revenue trends
- User growth
- Key KPIs
- Month-over-month comparison

**Product Dashboard:**
- Feature adoption
- User flows
- Engagement metrics
- Retention cohorts
- A/B test results

**Marketing Dashboard:**
- Acquisition channels
- Campaign performance
- Attribution analysis
- CAC and LTV
- Conversion funnels

**Dashboard Design Principles:**
- Single metric per viz
- Clear titles and labels
- Appropriate chart types
- Interactive filters
- Mobile responsive

#### Step 11: Set Up Alerts
**Alert Types:**
```
Anomaly Detection:
  - Sudden traffic spike/drop
  - Conversion rate change
  - Error rate increase
  
Threshold Alerts:
  - Revenue below target
  - Cart abandonment > 70%
  - Page load time > 3s
  
Goal Alerts:
  - Daily active users milestone
  - Revenue target achieved
  - Feature adoption goal
```

**Alert Configuration:**
```yaml
alert_name: "High Cart Abandonment"
condition: "cart_abandonment_rate > 0.75"
frequency: "hourly"
notification:
  - email: "product-team@company.com"
  - slack: "#alerts-product"
action: "Investigate checkout flow issues"
```

#### Step 12: Documentation and Training
**Documentation Components:**
- Tracking plan spreadsheet
- Implementation guides
- Event dictionary
- Dashboard user guides
- Troubleshooting docs

**Training Materials:**
```
For Developers:
  - SDK implementation guide
  - Event tracking best practices
  - Testing procedures
  - Code examples
  
For Product Teams:
  - Dashboard navigation
  - Metric definitions
  - Analysis techniques
  - Report creation
  
For Stakeholders:
  - KPI overview
  - Dashboard access
  - Insight interpretation
  - Decision frameworks
```

### Phase 5: Quality Assurance

#### Step 13: Testing and Validation
**Testing Checklist:**
- [ ] Events fire correctly
- [ ] Properties populated
- [ ] User identification works
- [ ] Cross-device tracking
- [ ] Data appears in dashboards
- [ ] No duplicate events
- [ ] Privacy compliance

**Validation Methods:**
```javascript
// Debug mode
analytics.debug(true);

// Event validation
function validateEvent(eventName, properties) {
  // Check required properties
  const required = ['user_id', 'session_id', 'timestamp'];
  const missing = required.filter(prop => !properties[prop]);
  
  if (missing.length > 0) {
    console.error(`Missing properties: ${missing.join(', ')}`);
    return false;
  }
  
  // Validate data types
  if (typeof properties.timestamp !== 'number') {
    console.error('Timestamp must be a number');
    return false;
  }
  
  return true;
}
```

#### Step 14: Data Quality Monitoring
**Quality Metrics:**
- Event volume trends
- Missing property rates
- Data freshness
- Duplicate event rate
- User identification rate

**Monitoring Dashboard:**
```sql
-- Check for data gaps
SELECT 
  DATE(event_timestamp) as date,
  COUNT(*) as event_count,
  COUNT(DISTINCT user_id) as unique_users
FROM events
WHERE event_timestamp >= CURRENT_DATE - 7
GROUP BY date
ORDER BY date DESC;

-- Identify missing properties
SELECT 
  event_name,
  COUNT(*) as total_events,
  SUM(CASE WHEN user_id IS NULL THEN 1 ELSE 0 END) as missing_user_id,
  SUM(CASE WHEN session_id IS NULL THEN 1 ELSE 0 END) as missing_session_id
FROM events
WHERE event_timestamp >= CURRENT_DATE - 1
GROUP BY event_name;
```

### Phase 6: Optimization and Maintenance

#### Step 15: Continuous Improvement
**Optimization Areas:**
- Query performance
- Dashboard load times
- Data pipeline efficiency
- Storage costs
- Alert accuracy

**Maintenance Schedule:**
```
Daily:
  - Check data pipeline health
  - Review critical metrics
  - Address alerts
  
Weekly:
  - Audit data quality
  - Update documentation
  - Review new tracking requests
  
Monthly:
  - Dashboard performance review
  - Tracking plan updates
  - Team training sessions
  
Quarterly:
  - Full analytics audit
  - Tool evaluation
  - Strategy alignment
```

## Advanced Analytics Concepts

### Attribution Modeling
**Models:**
- Last-click attribution
- First-click attribution
- Linear attribution
- Time-decay attribution
- Data-driven attribution

### Cohort Analysis
```sql
-- Retention cohort query
SELECT 
  cohort_month,
  months_since_signup,
  COUNT(DISTINCT user_id) as users,
  COUNT(DISTINCT user_id) / MAX(cohort_size) as retention_rate
FROM (
  SELECT 
    DATE_TRUNC('month', u.signup_date) as cohort_month,
    DATE_DIFF('month', u.signup_date, e.event_date) as months_since_signup,
    u.user_id,
    COUNT(u.user_id) OVER (PARTITION BY DATE_TRUNC('month', u.signup_date)) as cohort_size
  FROM users u
  JOIN events e ON u.user_id = e.user_id
  WHERE e.event_name = 'session_started'
)
GROUP BY cohort_month, months_since_signup
ORDER BY cohort_month, months_since_signup;
```

### Predictive Analytics
**Use Cases:**
- Churn prediction
- LTV estimation
- Conversion probability
- Recommendation engines

## Best Practices

### Privacy and Compliance
- Implement consent management
- Honor opt-outs
- Anonymize PII
- Follow GDPR/CCPA
- Document data retention

### Performance Optimization
- Batch event sending
- Compress payloads
- Use sampling for high-volume
- Implement caching
- Optimize queries

### Data Governance
- Single source of truth
- Version control tracking plans
- Regular audits
- Clear ownership
- Change management process

## Common Pitfalls

### Pitfall 1: Over-Tracking
**Problem:** Tracking everything without purpose
**Mitigation:** Start with key metrics, expand gradually

### Pitfall 2: Inconsistent Naming
**Problem:** Same event with different names
**Mitigation:** Enforce naming conventions, use tracking plan

### Pitfall 3: No Action on Data
**Problem:** Dashboards without decisions
**Mitigation:** Define actions for each metric

### Pitfall 4: Poor Data Quality
**Problem:** Incomplete or incorrect data
**Mitigation:** Implement validation, monitoring

## Success Metrics

### Implementation Success
- Tracking coverage: >95%
- Data accuracy: >99%
- Dashboard adoption: >80%
- Time to insight: <1 day
- Decision influence: >50%

### Business Impact
- Improved conversion rates
- Reduced churn
- Increased engagement
- Better feature adoption
- Faster decision making

## Templates and Resources

### Tracking Plan Template
```
Event Name | Description | Properties | When Triggered | Owner
-----------|-------------|------------|----------------|-------
user_signed_up | New user registration | user_id, signup_method, referral_source | On successful registration | Product
item_purchased | Purchase completed | item_id, price, quantity, payment_method | On payment confirmation | E-commerce
```

### Analytics Checklist
```
Pre-Launch:
[ ] Tracking plan reviewed
[ ] Events implemented
[ ] Testing complete
[ ] Dashboards created
[ ] Team trained

Post-Launch:
[ ] Data flowing correctly
[ ] Dashboards working
[ ] Alerts configured
[ ] Documentation updated
[ ] Stakeholders notified
```

## Related Resources

- **Agent Reference:** PHASE3-AGENT-003 (Product Manager)
- **Subagent:** metrics-analytics-lead for analysis
- **Related Workflows:** a-b-testing-workflow, feature-launch-checklist
- **Next Steps:** Dashboard creation, insight generation
- **Tools:** Segment, Amplitude, Mixpanel, Google Analytics

## Conclusion

Effective analytics setup is the foundation of data-driven product development. This comprehensive workflow provides the structure needed to implement robust analytics while maintaining flexibility for various product needs. Remember that analytics is not just about collecting data but about deriving actionable insights that drive product success. Build a culture of measurement, continuously refine your approach, and let data guide but not dictate your decisions.