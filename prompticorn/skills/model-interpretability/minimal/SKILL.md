# Model Interpretability (Minimal)

## Purpose
Explain what a trained model is doing — globally and for individual predictions —
without mistaking the explanation for a statement about the world.

## Core Techniques

### 1. Know What Kind of Explanation You Need
| Question | Tool |
|---|---|
| What drives the model overall? | Global SHAP summary, partial dependence |
| Why *this* prediction? | SHAP values for one row, counterfactuals |
| How does the model respond to feature x? | PDP, plus ICE curves for heterogeneity |
| Which features could I drop? | Permutation importance (see feature-importance-analysis) |

### 2. SHAP for Local Attribution
```python
import shap

explainer = shap.TreeExplainer(model)          # exact & fast for trees
sv = explainer(X_test)                          # Explanation object

shap.plots.waterfall(sv[0])                     # one prediction
shap.plots.beeswarm(sv)                         # global view
```
SHAP values are additive: `base_value + sum(shap_values) == model output`, in
log-odds for a binary tree classifier, not probability. Use `KernelExplainer`
only when nothing better exists — it is model-agnostic but slow, and it samples.

### 3. Partial Dependence with ICE
```python
from sklearn.inspection import PartialDependenceDisplay

PartialDependenceDisplay.from_estimator(
    model, X_test, features=["tenure", "monthly_charges"], kind="both"
)
```
`kind="both"` overlays individual (ICE) curves on the average. If the ICE lines
fan out in opposite directions, the flat PDP average is a lie — there is an
interaction hiding under it.

### 4. Remember: SHAP Explains the Model, Not the World
A SHAP value says "given this model, this feature moved the output by 0.4." It
does not say the feature *causes* the outcome. If `n_hospital_visits` proxies
disease severity, SHAP will credit the visits; intervening to reduce visits
changes nothing. Under correlated inputs the model may also have arbitrarily
assigned credit between two collinear features — a different seed can flip it.

### 5. Sanity-Check the Explanation
Train on shuffled labels: any feature still looking important reveals a bug in
the pipeline. Compare SHAP rankings across seeds — an unstable top-5 means you
are reading noise. Confirm a claimed driver by actually perturbing the input and
watching the prediction move.

### 6. Prefer a Glassbox When Stakes Justify It
Logistic regression with monotonic constraints, or an EBM/GAM, often costs 1-2
points of AUC and gives an explanation that is the model rather than an
approximation of it. In regulated adverse-action settings that trade is usually
correct.

## Warning Signs

- SHAP output described in causal language ("reducing x will reduce churn")
- Explanations produced for a model nobody validated for accuracy first
- Top features flipping between reruns and nobody noticing
- PDP shown without ICE on a model with known interactions
- `KernelExplainer` run on a tree model where `TreeExplainer` is exact
- A single background/reference dataset choice never questioned
