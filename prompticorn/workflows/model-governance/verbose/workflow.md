---
name: "model-governance"
description: "Establish governance processes for ML model lifecycle"
agent: "mlai"
category: "ml"
related_workflows:
  - model-evaluation-workflow
  - production-ml-deployment
  - mlops-pipeline-setup
---

# Model Governance Workflow - Comprehensive Guide

## Problem Context

Model governance ensures ML models comply with regulatory requirements, ethical standards, and business policies throughout their lifecycle. This involves establishing clear ownership, documentation standards, approval processes, and audit trails. Proper governance reduces risk, ensures compliance, and maintains trust in AI systems.

## Prerequisites

- Understanding of regulatory requirements (GDPR, CCPA, industry-specific)
- Defined organizational AI principles and ethics guidelines
- Model registry or management system
- Documentation templates and standards
- Risk assessment framework

## Step-by-Step Implementation

### Step 1: Establish Governance Framework

#### 1.1 Define Roles and Responsibilities
```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import datetime

@dataclass
class GovernanceRole:
    """Define roles in model governance."""
    
    role_name: str
    responsibilities: List[str]
    approval_authority: List[str]
    escalation_path: Optional[str]

class ModelGovernanceFramework:
    def __init__(self):
        self.roles = self._define_roles()
        self.approval_matrix = self._define_approval_matrix()
        
    def _define_roles(self) -> Dict[str, GovernanceRole]:
        """Define governance roles."""
        
        return {
            'model_owner': GovernanceRole(
                role_name='Model Owner',
                responsibilities=[
                    'Define model requirements',
                    'Approve model changes',
                    'Monitor model performance',
                    'Ensure compliance'
                ],
                approval_authority=['model_deployment', 'model_retirement'],
                escalation_path='ml_governance_board'
            ),
            'data_steward': GovernanceRole(
                role_name='Data Steward',
                responsibilities=[
                    'Ensure data quality',
                    'Manage data access',
                    'Validate data usage',
                    'Monitor data drift'
                ],
                approval_authority=['data_access', 'data_retention'],
                escalation_path='chief_data_officer'
            ),
            'ml_engineer': GovernanceRole(
                role_name='ML Engineer',
                responsibilities=[
                    'Develop and train models',
                    'Document model architecture',
                    'Implement monitoring',
                    'Maintain model code'
                ],
                approval_authority=['code_changes', 'feature_engineering'],
                escalation_path='ml_lead'
            ),
            'compliance_officer': GovernanceRole(
                role_name='Compliance Officer',
                responsibilities=[
                    'Review regulatory compliance',
                    'Approve high-risk models',
                    'Audit model decisions',
                    'Manage compliance documentation'
                ],
                approval_authority=['production_deployment', 'external_sharing'],
                escalation_path='legal_team'
            )
        }
```

### Step 2: Model Documentation Standards

#### 2.1 Create Model Card Template
```python
@dataclass
class ModelCard:
    """Model documentation standard."""
    
    # Model Details
    model_name: str
    version: str
    created_date: datetime.datetime
    last_modified: datetime.datetime
    model_type: str  # classification, regression, etc.
    
    # Intended Use
    primary_use_case: str
    intended_users: List[str]
    out_of_scope_uses: List[str]
    
    # Training Data
    training_data_description: str
    training_data_size: int
    data_collection_process: str
    data_preprocessing_steps: List[str]
    
    # Model Performance
    performance_metrics: Dict[str, float]
    evaluation_dataset: str
    performance_thresholds: Dict[str, float]
    
    # Ethical Considerations
    fairness_assessment: Dict[str, Any]
    bias_mitigation_steps: List[str]
    demographic_performance: Dict[str, Dict[str, float]]
    
    # Limitations and Risks
    known_limitations: List[str]
    failure_modes: List[str]
    risk_assessment: Dict[str, str]
    
    # Governance
    owner: str
    approvers: List[str]
    review_frequency: str
    compliance_requirements: List[str]
    
    def to_markdown(self) -> str:
        """Generate markdown documentation."""
        
        return f"""
# Model Card: {self.model_name} v{self.version}

## Model Details
- **Type:** {self.model_type}
- **Created:** {self.created_date}
- **Last Modified:** {self.last_modified}

## Intended Use
**Primary Use Case:** {self.primary_use_case}

**Intended Users:** {', '.join(self.intended_users)}

**Out of Scope:** {', '.join(self.out_of_scope_uses)}

## Performance Metrics
{self._format_metrics(self.performance_metrics)}

## Ethical Considerations
{self._format_fairness(self.fairness_assessment)}

## Limitations
{self._format_list(self.known_limitations)}

## Governance
- **Owner:** {self.owner}
- **Review Frequency:** {self.review_frequency}
        """
```

### Step 3: Risk Assessment and Classification

#### 3.1 Model Risk Framework
```python
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ModelRiskAssessment:
    def __init__(self):
        self.risk_factors = self._define_risk_factors()
        
    def assess_model_risk(self, model_metadata: Dict) -> Dict:
        """Assess model risk level."""
        
        risk_scores = {}
        
        # Impact assessment
        impact_score = self._assess_impact(
            model_metadata.get('use_case'),
            model_metadata.get('affected_users')
        )
        risk_scores['impact'] = impact_score
        
        # Data sensitivity
        data_score = self._assess_data_sensitivity(
            model_metadata.get('data_types'),
            model_metadata.get('pii_usage')
        )
        risk_scores['data_sensitivity'] = data_score
        
        # Model complexity
        complexity_score = self._assess_complexity(
            model_metadata.get('model_type'),
            model_metadata.get('interpretability')
        )
        risk_scores['complexity'] = complexity_score
        
        # Regulatory exposure
        regulatory_score = self._assess_regulatory_risk(
            model_metadata.get('regulations'),
            model_metadata.get('geography')
        )
        risk_scores['regulatory'] = regulatory_score
        
        # Calculate overall risk
        overall_risk = self._calculate_overall_risk(risk_scores)
        
        return {
            'risk_level': overall_risk,
            'risk_scores': risk_scores,
            'required_approvals': self._get_required_approvals(overall_risk),
            'audit_frequency': self._get_audit_frequency(overall_risk)
        }
```

### Step 4: Approval Workflow

#### 4.1 Multi-Stage Approval Process
```python
class ApprovalWorkflow:
    def __init__(self, model_card: ModelCard, risk_assessment: Dict):
        self.model_card = model_card
        self.risk_assessment = risk_assessment
        self.approval_stages = self._define_approval_stages()
        self.approval_history = []
        
    def _define_approval_stages(self) -> List[Dict]:
        """Define approval stages based on risk."""
        
        risk_level = self.risk_assessment['risk_level']
        
        stages = [
            {
                'stage': 'technical_review',
                'approvers': ['ml_lead', 'data_engineer'],
                'criteria': [
                    'Model performance meets thresholds',
                    'Code quality standards met',
                    'Documentation complete'
                ]
            },
            {
                'stage': 'business_review',
                'approvers': ['product_owner', 'business_stakeholder'],
                'criteria': [
                    'Aligns with business objectives',
                    'ROI justification',
                    'User acceptance criteria met'
                ]
            }
        ]
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            stages.append({
                'stage': 'compliance_review',
                'approvers': ['compliance_officer', 'legal_team'],
                'criteria': [
                    'Regulatory compliance verified',
                    'Privacy impact assessment complete',
                    'Ethical review passed'
                ]
            })
        
        if risk_level == RiskLevel.CRITICAL:
            stages.append({
                'stage': 'executive_approval',
                'approvers': ['cto', 'cro'],
                'criteria': [
                    'Strategic alignment',
                    'Risk-reward assessment',
                    'Board notification if required'
                ]
            })
        
        return stages
    
    def submit_for_approval(self, stage: str, approver: str, decision: str, comments: str):
        """Record approval decision."""
        
        approval_record = {
            'timestamp': datetime.datetime.now(),
            'stage': stage,
            'approver': approver,
            'decision': decision,  # approved, rejected, conditional
            'comments': comments,
            'model_version': self.model_card.version
        }
        
        self.approval_history.append(approval_record)
        
        # Check if stage is complete
        if self._is_stage_complete(stage):
            return self._advance_to_next_stage()
        
        return {'status': 'pending', 'current_stage': stage}
```

### Step 5: Audit Trail and Compliance

#### 5.1 Comprehensive Audit Logging
```python
import hashlib
import json

class ModelAuditTrail:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.audit_log = []
        
    def log_event(self, event_type: str, details: Dict, user: str):
        """Log governance event with immutable audit trail."""
        
        event = {
            'event_id': self._generate_event_id(),
            'timestamp': datetime.datetime.now().isoformat(),
            'model_id': self.model_id,
            'event_type': event_type,
            'user': user,
            'details': details,
            'checksum': None
        }
        
        # Create checksum for integrity
        event['checksum'] = self._calculate_checksum(event)
        
        self.audit_log.append(event)
        
        # Persist to immutable storage
        self._persist_to_storage(event)
        
        return event['event_id']
    
    def _calculate_checksum(self, event: Dict) -> str:
        """Calculate event checksum."""
        
        event_str = json.dumps(event, sort_keys=True, default=str)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def verify_audit_trail(self) -> bool:
        """Verify audit trail integrity."""
        
        for event in self.audit_log:
            original_checksum = event['checksum']
            event_copy = event.copy()
            event_copy['checksum'] = None
            
            calculated_checksum = self._calculate_checksum(event_copy)
            
            if calculated_checksum != original_checksum:
                return False
        
        return True
```

### Step 6: Model Lifecycle Management

#### 6.1 Lifecycle States and Transitions
```python
class ModelLifecycle:
    def __init__(self):
        self.states = {
            'development': {
                'next_states': ['validation'],
                'requirements': ['initial_documentation']
            },
            'validation': {
                'next_states': ['approved', 'rejected', 'development'],
                'requirements': ['performance_validation', 'risk_assessment']
            },
            'approved': {
                'next_states': ['staging'],
                'requirements': ['approval_complete', 'deployment_plan']
            },
            'staging': {
                'next_states': ['production', 'approved'],
                'requirements': ['integration_testing', 'performance_testing']
            },
            'production': {
                'next_states': ['monitoring', 'deprecated'],
                'requirements': ['monitoring_setup', 'sla_defined']
            },
            'monitoring': {
                'next_states': ['retraining', 'deprecated'],
                'requirements': ['performance_monitoring', 'drift_detection']
            },
            'deprecated': {
                'next_states': ['archived'],
                'requirements': ['migration_plan', 'sunset_notification']
            },
            'archived': {
                'next_states': [],
                'requirements': ['data_retention_compliance']
            }
        }
    
    def transition_model(self, model_id: str, current_state: str, target_state: str) -> Dict:
        """Manage model state transitions."""
        
        # Validate transition
        if target_state not in self.states[current_state]['next_states']:
            return {
                'success': False,
                'error': f'Invalid transition from {current_state} to {target_state}'
            }
        
        # Check requirements
        requirements = self.states[target_state]['requirements']
        missing_requirements = self._check_requirements(model_id, requirements)
        
        if missing_requirements:
            return {
                'success': False,
                'missing_requirements': missing_requirements
            }
        
        # Execute transition
        self._execute_transition(model_id, current_state, target_state)
        
        return {
            'success': True,
            'new_state': target_state,
            'timestamp': datetime.datetime.now()
        }
```

### Step 7: Monitoring and Review

#### 7.1 Ongoing Governance Monitoring
```python
class GovernanceMonitor:
    def __init__(self, review_schedule: Dict):
        self.review_schedule = review_schedule
        self.review_history = []
        
    def schedule_review(self, model_id: str, risk_level: RiskLevel):
        """Schedule governance reviews based on risk."""
        
        frequency_map = {
            RiskLevel.LOW: 'annually',
            RiskLevel.MEDIUM: 'quarterly',
            RiskLevel.HIGH: 'monthly',
            RiskLevel.CRITICAL: 'weekly'
        }
        
        review_schedule = {
            'model_id': model_id,
            'frequency': frequency_map[risk_level],
            'next_review': self._calculate_next_review(frequency_map[risk_level]),
            'review_checklist': self._get_review_checklist(risk_level)
        }
        
        return review_schedule
    
    def conduct_review(self, model_id: str, reviewer: str) -> Dict:
        """Conduct governance review."""
        
        review_items = [
            self._check_performance_degradation(model_id),
            self._check_data_drift(model_id),
            self._check_compliance_changes(model_id),
            self._check_incident_reports(model_id),
            self._verify_documentation_current(model_id)
        ]
        
        review_result = {
            'model_id': model_id,
            'reviewer': reviewer,
            'timestamp': datetime.datetime.now(),
            'items_reviewed': review_items,
            'issues_found': [item for item in review_items if not item['passed']],
            'recommendations': self._generate_recommendations(review_items)
        }
        
        self.review_history.append(review_result)
        
        return review_result
```

## Best Practices

1. **Clear Ownership:** Every model must have a designated owner
2. **Documentation First:** Complete documentation before deployment
3. **Risk-Based Approach:** Governance rigor proportional to risk
4. **Continuous Monitoring:** Regular reviews and updates
5. **Audit Everything:** Maintain immutable audit trails
6. **Automate Compliance:** Use tools to enforce policies

## Anti-Patterns to Avoid

1. **Governance Theater:** Process without substance
2. **One-Size-Fits-All:** Same process for all risk levels
3. **Documentation Lag:** Documentation after deployment
4. **No Enforcement:** Policies without teeth
5. **Siloed Governance:** Disconnected from development

## Integration Points

- **Model Registry:** Central repository for all models
- **CI/CD Pipeline:** Automated governance checks
- **Monitoring Systems:** Performance and compliance tracking
- **Documentation Systems:** Version-controlled documentation

## Troubleshooting

### Issue: Slow approval process
**Solution:** Implement risk-based fast tracks, automate low-risk approvals

### Issue: Documentation drift
**Solution:** Automate documentation generation, regular audits

### Issue: Compliance violations
**Solution:** Automated compliance checks, training programs

## Related Workflows

- [Model Evaluation Workflow](../model-evaluation-workflow) for performance validation
- [Production ML Deployment](../production-ml-deployment) for deployment governance
- [MLOps Pipeline Setup](../mlops-pipeline-setup) for automated governance