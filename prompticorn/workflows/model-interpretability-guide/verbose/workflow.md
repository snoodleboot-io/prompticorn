---
name: "model-interpretability-guide"
description: Make ML models interpretable and explainable for stakeholders and debugging
type: workflow
category: workflow-patterns
minimal: false
---

# Model Interpretability Guide

## Overview
Interpreting model decisions is crucial for debugging, trust, and regulatory compliance.

## Model-Agnostic Methods

### LIME (Local Interpretable Model-Agnostic Explanations)
- Explains individual predictions
- Creates local linear approximation
- Works with any model
- Feature importance for prediction

### SHAP (SHapley Additive exPlanations)
- Game theory approach
- Feature contribution to prediction
- Consistent and locally accurate
- Multiple interpretation plots

### Feature Importance
- Permutation importance
- Drop-column importance
- Gain-based importance
- Understand feature relevance

### Attention Mechanisms
- For neural networks
- Shows which input attended to
- Visualization of focus
- Interpretable intermediate steps

## Model-Specific Interpretation

### Linear Models
- Coefficients show direction/magnitude
- Directly interpretable
- Easy to understand
- No approximation needed

### Tree-Based Models
- Feature importance built-in
- Decision paths explainable
- Prediction rules extractable
- Visual interpretation possible

### Neural Networks
- Activation visualization
- Gradient-based analysis
- Saliency maps
- Hidden layer analysis

## Visualization Approaches

### Feature Importance Plots
- Bar charts of feature contributions
- Global view of important features
- Quick model understanding

### Partial Dependence Plots
- Feature vs predicted output
- Non-linear relationships
- Interaction effects
- Intuitive interpretation

### Individual Explanation Plots
- SHAP force plots
- Decision trees for path
- Feature attribution
- Per-sample explanations

## Testing for Interpretability

### Fairness Analysis
- Bias across groups
- Disparate impact
- Fairness metrics
- Mitigation strategies

### Robustness Testing
- Adversarial examples
- Sensitivity to input changes
- Model stability
- Failure modes

### Consistency Checks
- Similar inputs → similar outputs
- Edge case behavior
- Logical consistency
- Real-world alignment

## Regulatory Compliance

### GDPR Right to Explanation
- Right to understand automated decisions
- System explanations required
- Plain language needed
- Individual request handling

### Model Documentation
- Training data description
- Feature engineering rationale
- Performance metrics
- Limitations and biases

## Best Practices

1. **Interpret during development:** Not just after
2. **Multiple methods:** No single best interpretation
3. **Involve domain experts:** Validate interpretations
4. **Document assumptions:** What model is assuming
5. **User testing:** Can users understand explanations
6. **Regular review:** Detect model drift
7. **Transparent limitations:** Known biases and failure modes
