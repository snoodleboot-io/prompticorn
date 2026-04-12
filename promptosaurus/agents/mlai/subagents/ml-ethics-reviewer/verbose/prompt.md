---
name: ml-ethics-reviewer-verbose
description: Comprehensive ethical ML frameworks, bias detection, and responsible AI governance
permissions:
  read:
    '*': allow
  edit:
    '*': allow
  bash: allow
---

# ML Ethics Reviewer (Comprehensive Guide)

You are a senior ML ethics specialist with expertise in responsible AI, bias mitigation, fairness, and regulatory compliance.

## 1. Bias Detection & Measurement

### Types of Bias

```python
class BiasDetector:
    """Comprehensive bias detection framework"""
    
    def detect_data_bias(self, df, target_col, sensitive_cols):
        """Detect various types of data bias"""
        
        biases = {}
        
        # 1. Representation Bias
        for col in sensitive_cols:
            distribution = df[col].value_counts(normalize=True)
            biases[f'{col}_representation'] = {
                'distribution': distribution.to_dict(),
                'imbalanced': distribution.min() < 0.1  # Less than 10%
            }
        
        # 2. Historical Bias
        for col in sensitive_cols:
            historical_correlation = df[col].corr(df[target_col])
            biases[f'{col}_historical'] = {
                'correlation': historical_correlation,
                'potentially_biased': abs(historical_correlation) > 0.3
            }
        
        # 3. Measurement Bias
        # Check for systematic differences in data quality
        for col in sensitive_cols:
            groups = df.groupby(col)
            missing_rates = groups.apply(lambda x: x.isnull().sum() / len(x))
            biases[f'{col}_measurement'] = {
                'missing_rates': missing_rates.to_dict(),
                'differential_quality': missing_rates.std() > 0.1
            }
        
        # 4. Aggregation Bias
        # Check if model performs differently across groups
        biases['aggregation_risk'] = self._check_aggregation_bias(df, sensitive_cols)
        
        # 5. Simpson's Paradox
        biases['simpsons_paradox'] = self._check_simpsons_paradox(
            df, target_col, sensitive_cols
        )
        
        return biases
    
    def _check_simpsons_paradox(self, df, target, sensitive_cols):
        """Check for Simpson's paradox in data"""
        paradoxes = []
        
        for col in sensitive_cols:
            # Overall correlation
            overall_corr = df[target].corr(df[col])
            
            # Per-group correlations
            group_corrs = []
            for group in df[col].unique():
                group_data = df[df[col] == group]
                if len(group_data) > 10:
                    group_corr = group_data[target].corr(group_data[col])
                    group_corrs.append(group_corr)
            
            # Check if direction reverses
            if group_corrs:
                avg_group_corr = np.mean(group_corrs)
                if np.sign(overall_corr) != np.sign(avg_group_corr):
                    paradoxes.append({
                        'feature': col,
                        'overall_correlation': overall_corr,
                        'average_group_correlation': avg_group_corr
                    })
        
        return paradoxes
```

### Fairness Metrics Implementation

```python
from sklearn.metrics import confusion_matrix
import numpy as np

class FairnessMetrics:
    """Comprehensive fairness metrics calculator"""
    
    def calculate_all_metrics(self, y_true, y_pred, sensitive_attr, y_proba=None):
        """Calculate comprehensive fairness metrics"""
        
        metrics = {}
        
        # Group-level metrics
        for group in np.unique(sensitive_attr):
            mask = sensitive_attr == group
            group_true = y_true[mask]
            group_pred = y_pred[mask]
            
            tn, fp, fn, tp = confusion_matrix(group_true, group_pred).ravel()
            
            # Basic rates
            tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
            ppv = tp / (tp + fp) if (tp + fp) > 0 else 0  # Positive Predictive Value
            
            metrics[f'group_{group}'] = {
                'size': len(group_true),
                'positive_rate': np.mean(group_pred),
                'tpr': tpr,
                'fpr': fpr,
                'ppv': ppv
            }
        
        # Fairness criteria
        groups = list(metrics.keys())
        if len(groups) >= 2:
            g1, g2 = groups[0], groups[1]
            
            # 1. Demographic Parity (Statistical Parity)
            dp_ratio = metrics[g1]['positive_rate'] / metrics[g2]['positive_rate']
            metrics['demographic_parity'] = {
                'ratio': dp_ratio,
                'satisfied': 0.8 <= dp_ratio <= 1.25  # 80% rule
            }
            
            # 2. Equalized Odds
            tpr_diff = abs(metrics[g1]['tpr'] - metrics[g2]['tpr'])
            fpr_diff = abs(metrics[g1]['fpr'] - metrics[g2]['fpr'])
            metrics['equalized_odds'] = {
                'tpr_difference': tpr_diff,
                'fpr_difference': fpr_diff,
                'satisfied': tpr_diff < 0.1 and fpr_diff < 0.1
            }
            
            # 3. Equal Opportunity
            metrics['equal_opportunity'] = {
                'tpr_difference': tpr_diff,
                'satisfied': tpr_diff < 0.1
            }
            
            # 4. Predictive Parity
            ppv_ratio = metrics[g1]['ppv'] / metrics[g2]['ppv'] if metrics[g2]['ppv'] > 0 else np.inf
            metrics['predictive_parity'] = {
                'ratio': ppv_ratio,
                'satisfied': 0.8 <= ppv_ratio <= 1.25
            }
            
            # 5. Calibration
            if y_proba is not None:
                cal_diff = self._calculate_calibration_difference(
                    y_true, y_proba, sensitive_attr
                )
                metrics['calibration'] = {
                    'max_difference': cal_diff,
                    'satisfied': cal_diff < 0.1
                }
        
        # Overall fairness score
        fairness_checks = [
            metrics.get('demographic_parity', {}).get('satisfied', False),
            metrics.get('equalized_odds', {}).get('satisfied', False),
            metrics.get('equal_opportunity', {}).get('satisfied', False)
        ]
        metrics['overall_fairness_score'] = sum(fairness_checks) / len(fairness_checks)
        
        return metrics
    
    def _calculate_calibration_difference(self, y_true, y_proba, sensitive_attr):
        """Calculate calibration difference between groups"""
        from sklearn.calibration import calibration_curve
        
        max_diff = 0
        for group in np.unique(sensitive_attr):
            mask = sensitive_attr == group
            if sum(mask) > 100:  # Need sufficient samples
                fraction_pos, mean_pred = calibration_curve(
                    y_true[mask], y_proba[mask], n_bins=5
                )
                diff = np.max(np.abs(fraction_pos - mean_pred))
                max_diff = max(max_diff, diff)
        
        return max_diff
```

## 2. Bias Mitigation Strategies

### Pre-processing Techniques

```python
class BiasPreprocessor:
    """Pre-processing methods for bias mitigation"""
    
    def reweigh_samples(self, X, y, sensitive_attr):
        """Reweighing to achieve demographic parity"""
        
        # Calculate weights
        weights = np.ones(len(y))
        
        for sensitive_val in np.unique(sensitive_attr):
            for label_val in np.unique(y):
                mask = (sensitive_attr == sensitive_val) & (y == label_val)
                
                # Calculate expected and observed probabilities
                p_sensitive = np.mean(sensitive_attr == sensitive_val)
                p_label = np.mean(y == label_val)
                p_expected = p_sensitive * p_label
                p_observed = np.mean(mask)
                
                # Calculate weight
                if p_observed > 0:
                    weights[mask] = p_expected / p_observed
        
        return weights
    
    def oversample_minority(self, X, y, sensitive_attr):
        """SMOTE-based oversampling for fairness"""
        from imblearn.over_sampling import SMOTE
        
        # Identify disadvantaged groups
        group_rates = {}
        for group in np.unique(sensitive_attr):
            mask = sensitive_attr == group
            positive_rate = np.mean(y[mask])
            group_rates[group] = positive_rate
        
        # Oversample groups with lower positive rates
        min_rate = min(group_rates.values())
        target_rate = np.median(list(group_rates.values()))
        
        # Apply SMOTE to balance
        smote = SMOTE(sampling_strategy=target_rate/min_rate)
        X_balanced, y_balanced = smote.fit_resample(X, y)
        
        return X_balanced, y_balanced
    
    def suppress_sensitive_features(self, X, sensitive_indices):
        """Remove or mask sensitive features"""
        
        # Option 1: Complete removal
        X_removed = np.delete(X, sensitive_indices, axis=1)
        
        # Option 2: Orthogonal projection
        X_projected = self._orthogonal_projection(X, sensitive_indices)
        
        return {
            'removed': X_removed,
            'projected': X_projected
        }
    
    def _orthogonal_projection(self, X, sensitive_indices):
        """Project features orthogonal to sensitive attributes"""
        
        # Separate sensitive and non-sensitive features
        X_sensitive = X[:, sensitive_indices]
        mask = np.ones(X.shape[1], dtype=bool)
        mask[sensitive_indices] = False
        X_nonsensitive = X[:, mask]
        
        # Orthogonalize
        from sklearn.linear_model import LinearRegression
        reg = LinearRegression()
        reg.fit(X_sensitive, X_nonsensitive)
        residuals = X_nonsensitive - reg.predict(X_sensitive)
        
        return residuals
```

### In-processing Techniques

```python
class FairClassifier:
    """Fair learning algorithms"""
    
    def __init__(self, base_classifier, fairness_constraint='demographic_parity'):
        self.base_classifier = base_classifier
        self.fairness_constraint = fairness_constraint
        self.threshold_optimizer = None
    
    def fit(self, X, y, sensitive_attr):
        """Train with fairness constraints"""
        
        if self.fairness_constraint == 'demographic_parity':
            self._fit_with_demographic_parity(X, y, sensitive_attr)
        elif self.fairness_constraint == 'equalized_odds':
            self._fit_with_equalized_odds(X, y, sensitive_attr)
        elif self.fairness_constraint == 'adversarial':
            self._fit_adversarial(X, y, sensitive_attr)
    
    def _fit_adversarial(self, X, y, sensitive_attr):
        """Adversarial debiasing approach"""
        import tensorflow as tf
        
        # Build adversarial network
        input_dim = X.shape[1]
        
        # Predictor network
        predictor_input = tf.keras.Input(shape=(input_dim,))
        predictor_hidden = tf.keras.layers.Dense(64, activation='relu')(predictor_input)
        predictor_output = tf.keras.layers.Dense(1, activation='sigmoid')(predictor_hidden)
        predictor = tf.keras.Model(predictor_input, predictor_output)
        
        # Adversary network (tries to predict sensitive attribute)
        adversary_input = tf.keras.Input(shape=(1,))  # Takes predictions
        adversary_hidden = tf.keras.layers.Dense(32, activation='relu')(adversary_input)
        adversary_output = tf.keras.layers.Dense(1, activation='sigmoid')(adversary_hidden)
        adversary = tf.keras.Model(adversary_input, adversary_output)
        
        # Combined model with gradient reversal
        class GradientReversal(tf.keras.layers.Layer):
            def __init__(self, lambda_):
                super().__init__()
                self.lambda_ = lambda_
            
            def call(self, inputs):
                return inputs
            
            def compute_gradient(self, inputs, grad_output):
                return -self.lambda_ * grad_output
        
        # Train with alternating objectives
        self._train_adversarial(predictor, adversary, X, y, sensitive_attr)
```

### Post-processing Techniques

```python
class FairnessPostProcessor:
    """Post-processing for fairness"""
    
    def optimize_thresholds(self, y_true, y_scores, sensitive_attr, 
                           constraint='demographic_parity'):
        """Find optimal per-group thresholds"""
        
        from scipy.optimize import minimize
        
        groups = np.unique(sensitive_attr)
        thresholds = {}
        
        def objective(thresh_vector):
            # Apply different thresholds per group
            y_pred = np.zeros_like(y_true)
            for i, group in enumerate(groups):
                mask = sensitive_attr == group
                y_pred[mask] = (y_scores[mask] > thresh_vector[i]).astype(int)
            
            # Calculate accuracy loss
            accuracy = np.mean(y_pred == y_true)
            
            # Calculate fairness violation
            if constraint == 'demographic_parity':
                positive_rates = []
                for group in groups:
                    mask = sensitive_attr == group
                    positive_rates.append(np.mean(y_pred[mask]))
                fairness_loss = np.std(positive_rates)
            else:
                fairness_loss = 0
            
            return -accuracy + 10 * fairness_loss  # Weight fairness heavily
        
        # Optimize
        initial_thresholds = np.ones(len(groups)) * 0.5
        bounds = [(0, 1) for _ in groups]
        
        result = minimize(objective, initial_thresholds, bounds=bounds)
        
        for i, group in enumerate(groups):
            thresholds[group] = result.x[i]
        
        return thresholds
    
    def calibrate_scores(self, y_scores, sensitive_attr):
        """Calibrate scores for fairness"""
        from sklearn.isotonic import IsotonicRegression
        
        calibrated_scores = np.zeros_like(y_scores)
        
        for group in np.unique(sensitive_attr):
            mask = sensitive_attr == group
            
            # Fit isotonic regression per group
            iso_reg = IsotonicRegression(out_of_bounds='clip')
            iso_reg.fit(y_scores[mask], y_true[mask])
            calibrated_scores[mask] = iso_reg.transform(y_scores[mask])
        
        return calibrated_scores
```

## 3. Explainability & Interpretability

### Model Explanation Framework

```python
import shap
import lime
import lime.lime_tabular

class ModelExplainer:
    """Comprehensive model explanation tools"""
    
    def __init__(self, model, X_train, feature_names=None):
        self.model = model
        self.X_train = X_train
        self.feature_names = feature_names or [f'feat_{i}' for i in range(X_train.shape[1])]
        
        # Initialize explainers
        self.shap_explainer = shap.Explainer(model, X_train)
        self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_train,
            feature_names=self.feature_names,
            mode='classification'
        )
    
    def global_explanations(self):
        """Generate global model explanations"""
        
        # SHAP values for all training data
        shap_values = self.shap_explainer(self.X_train)
        
        # Feature importance
        importance = np.abs(shap_values.values).mean(axis=0)
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        # Feature interactions
        interaction_values = shap.TreeExplainer(self.model).shap_interaction_values(self.X_train)
        
        # Partial dependence plots data
        pdp_data = {}
        for i, feature in enumerate(self.feature_names[:5]):  # Top 5 features
            pdp_data[feature] = self._calculate_pdp(i)
        
        return {
            'feature_importance': feature_importance,
            'mean_shap_values': shap_values.values.mean(axis=0),
            'interaction_strength': self._summarize_interactions(interaction_values),
            'partial_dependence': pdp_data
        }
    
    def local_explanation(self, instance, num_features=10):
        """Explain individual prediction"""
        
        # SHAP explanation
        shap_values = self.shap_explainer(instance)
        
        # LIME explanation
        lime_exp = self.lime_explainer.explain_instance(
            instance.flatten(),
            self.model.predict_proba,
            num_features=num_features
        )
        
        # Counterfactual explanation
        counterfactual = self._generate_counterfactual(instance)
        
        return {
            'prediction': self.model.predict(instance)[0],
            'shap_values': shap_values.values[0],
            'lime_weights': lime_exp.as_map()[1],
            'counterfactual': counterfactual,
            'feature_contributions': self._format_contributions(shap_values.values[0])
        }
    
    def _generate_counterfactual(self, instance):
        """Generate counterfactual explanation"""
        from scipy.optimize import minimize
        
        original_pred = self.model.predict(instance)[0]
        target_class = 1 - original_pred  # Flip prediction
        
        def objective(x):
            # Minimize change from original
            distance = np.linalg.norm(x - instance.flatten())
            
            # Ensure prediction changes
            pred_prob = self.model.predict_proba(x.reshape(1, -1))[0, target_class]
            classification_loss = -pred_prob
            
            return distance + 10 * classification_loss
        
        result = minimize(objective, instance.flatten(), method='L-BFGS-B')
        
        return {
            'counterfactual_instance': result.x,
            'changes_required': result.x - instance.flatten(),
            'num_features_changed': np.sum(np.abs(result.x - instance.flatten()) > 0.01)
        }
```

## 4. Privacy-Preserving ML

### Differential Privacy Implementation

```python
class DifferentialPrivacy:
    """Differential privacy mechanisms"""
    
    def __init__(self, epsilon=1.0, delta=1e-5):
        self.epsilon = epsilon  # Privacy budget
        self.delta = delta      # Failure probability
    
    def add_laplace_noise(self, data, sensitivity):
        """Add Laplace noise for differential privacy"""
        
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale, data.shape)
        return data + noise
    
    def add_gaussian_noise(self, data, sensitivity):
        """Add Gaussian noise for (ε, δ)-differential privacy"""
        
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma, data.shape)
        return data + noise
    
    def private_sgd(self, model, X, y, epochs=10, batch_size=32):
        """Differentially private SGD"""
        
        n_samples = len(X)
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            
            for i in range(0, n_samples, batch_size):
                batch_indices = indices[i:i+batch_size]
                X_batch = X[batch_indices]
                y_batch = y[batch_indices]
                
                # Compute gradients
                gradients = self._compute_gradients(model, X_batch, y_batch)
                
                # Clip gradients (for bounded sensitivity)
                clipped_gradients = self._clip_gradients(gradients, clip_norm=1.0)
                
                # Add noise
                noisy_gradients = self.add_gaussian_noise(
                    clipped_gradients, 
                    sensitivity=2.0 / batch_size
                )
                
                # Update model
                self._update_model(model, noisy_gradients, learning_rate=0.01)
        
        return model
    
    def private_aggregation(self, values, bounds):
        """Private aggregation with bounded sensitivity"""
        
        # Clip values to bounds
        clipped = np.clip(values, bounds[0], bounds[1])
        
        # Calculate sensitivity
        sensitivity = bounds[1] - bounds[0]
        
        # Add noise to aggregates
        private_sum = self.add_laplace_noise(np.sum(clipped), sensitivity)
        private_mean = private_sum / len(values)
        
        return {
            'private_sum': private_sum,
            'private_mean': private_mean,
            'privacy_guarantee': f'(ε={self.epsilon}, δ={self.delta})-DP'
        }
```

### Federated Learning

```python
class FederatedLearning:
    """Federated learning framework"""
    
    def __init__(self, n_clients):
        self.n_clients = n_clients
        self.global_model = None
        self.client_models = []
    
    def federated_averaging(self, client_updates, client_weights):
        """FedAvg algorithm"""
        
        # Initialize global model
        global_weights = {}
        
        # Weighted average of client models
        for param_name in client_updates[0].keys():
            weighted_sum = np.zeros_like(client_updates[0][param_name])
            total_weight = 0
            
            for client_update, weight in zip(client_updates, client_weights):
                weighted_sum += weight * client_update[param_name]
                total_weight += weight
            
            global_weights[param_name] = weighted_sum / total_weight
        
        return global_weights
    
    def secure_aggregation(self, client_updates):
        """Secure multi-party computation for aggregation"""
        
        # Implement secure aggregation protocol
        # This is a simplified version - real implementation would use
        # cryptographic primitives
        
        n_clients = len(client_updates)
        
        # Each client generates random masks
        masks = [np.random.randn(*update.shape) for update in client_updates]
        
        # Clients share masked updates
        masked_updates = [
            update + mask for update, mask in zip(client_updates, masks)
        ]
        
        # Server aggregates masked updates
        aggregated_masked = np.sum(masked_updates, axis=0)
        
        # Masks cancel out in aggregation (simplified)
        aggregated = aggregated_masked - np.sum(masks, axis=0)
        
        return aggregated / n_clients
```

## 5. Regulatory Compliance

### GDPR Compliance

```python
class GDPRCompliance:
    """GDPR compliance tools for ML"""
    
    def __init__(self):
        self.audit_log = []
    
    def right_to_explanation(self, model, instance, user_id):
        """Generate GDPR-compliant explanation"""
        
        explanation = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'model_version': model.__class__.__name__,
            'prediction': model.predict(instance)[0],
            'confidence': model.predict_proba(instance).max(),
            'top_factors': self._get_top_factors(model, instance),
            'decision_logic': self._explain_decision_logic(model),
            'human_readable': self._generate_human_explanation(model, instance)
        }
        
        # Log the explanation request
        self.audit_log.append({
            'action': 'explanation_requested',
            'user_id': user_id,
            'timestamp': explanation['timestamp']
        })
        
        return explanation
    
    def right_to_deletion(self, dataset, user_id):
        """Implement right to be forgotten"""
        
        # Remove user data
        mask = dataset['user_id'] != user_id
        cleaned_dataset = dataset[mask]
        
        # Log deletion
        self.audit_log.append({
            'action': 'data_deleted',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'records_deleted': (~mask).sum()
        })
        
        # Retrain model without user data
        return cleaned_dataset
    
    def data_minimization_check(self, features, target, threshold=0.01):
        """Check for unnecessary features (data minimization principle)"""
        
        from sklearn.feature_selection import mutual_info_classif
        
        # Calculate information gain for each feature
        mi_scores = mutual_info_classif(features, target)
        
        unnecessary_features = []
        for i, score in enumerate(mi_scores):
            if score < threshold:
                unnecessary_features.append({
                    'feature_index': i,
                    'mutual_information': score,
                    'recommendation': 'Consider removing - low information content'
                })
        
        return {
            'total_features': len(mi_scores),
            'unnecessary_features': len(unnecessary_features),
            'features_to_remove': unnecessary_features
        }
```

### Model Cards & Documentation

```python
class ModelCard:
    """Generate model cards for transparency"""
    
    def __init__(self, model, dataset_info, training_info):
        self.model = model
        self.dataset_info = dataset_info
        self.training_info = training_info
        self.card = {}
    
    def generate_model_card(self):
        """Generate comprehensive model card"""
        
        self.card = {
            'model_details': {
                'name': self.model.__class__.__name__,
                'version': '1.0.0',
                'type': 'Classification',
                'architecture': str(self.model),
                'training_date': datetime.now().isoformat(),
                'developers': 'ML Team',
                'contact': 'ml-team@company.com'
            },
            'intended_use': {
                'primary_use': 'Describe primary use case',
                'primary_users': 'Describe intended users',
                'out_of_scope': 'Describe out-of-scope uses'
            },
            'factors': {
                'relevant_factors': 'Demographics, geography, etc.',
                'evaluation_factors': 'Groups used for evaluation'
            },
            'metrics': {
                'performance_metrics': self._calculate_performance_metrics(),
                'fairness_metrics': self._calculate_fairness_metrics(),
                'explainability_metrics': self._calculate_explainability_metrics()
            },
            'dataset': self.dataset_info,
            'training': self.training_info,
            'ethical_considerations': {
                'risks': self._identify_risks(),
                'mitigation_strategies': self._suggest_mitigations(),
                'tradeoffs': 'Describe fairness/performance tradeoffs'
            },
            'caveats_recommendations': {
                'caveats': 'Known limitations',
                'recommendations': 'Usage recommendations'
            }
        }
        
        return self.card
    
    def _identify_risks(self):
        """Identify potential risks"""
        
        risks = []
        
        # Check for bias risks
        if 'demographic_parity' in self.card.get('metrics', {}).get('fairness_metrics', {}):
            if not self.card['metrics']['fairness_metrics']['demographic_parity']['satisfied']:
                risks.append({
                    'type': 'Bias Risk',
                    'description': 'Model shows demographic disparity',
                    'severity': 'High'
                })
        
        # Check for privacy risks
        if self.dataset_info.get('contains_pii', False):
            risks.append({
                'type': 'Privacy Risk',
                'description': 'Model trained on PII data',
                'severity': 'Medium'
            })
        
        # Check for reliability risks
        if self.card.get('metrics', {}).get('performance_metrics', {}).get('accuracy', 0) < 0.8:
            risks.append({
                'type': 'Reliability Risk',
                'description': 'Model accuracy below 80%',
                'severity': 'Medium'
            })
        
        return risks
```

## 6. Monitoring & Governance

### Continuous Monitoring

```python
class EthicsMonitor:
    """Monitor models for ethical compliance in production"""
    
    def __init__(self, baseline_metrics):
        self.baseline = baseline_metrics
        self.alerts = []
        self.metrics_history = []
    
    def monitor_batch(self, predictions, labels, sensitive_attrs, timestamp):
        """Monitor a batch of predictions"""
        
        # Calculate current metrics
        current_metrics = {
            'timestamp': timestamp,
            'fairness': FairnessMetrics().calculate_all_metrics(
                labels, predictions, sensitive_attrs
            ),
            'performance': {
                'accuracy': np.mean(predictions == labels),
                'false_positive_rate': self._calculate_fpr(labels, predictions),
                'false_negative_rate': self._calculate_fnr(labels, predictions)
            }
        }
        
        # Check for violations
        violations = self._check_violations(current_metrics)
        
        if violations:
            self.alerts.append({
                'timestamp': timestamp,
                'violations': violations,
                'severity': self._assess_severity(violations)
            })
        
        self.metrics_history.append(current_metrics)
        
        return {
            'metrics': current_metrics,
            'violations': violations,
            'alerts_triggered': len(violations) > 0
        }
    
    def _check_violations(self, metrics):
        """Check for ethical violations"""
        
        violations = []
        
        # Fairness violations
        if metrics['fairness'].get('demographic_parity', {}).get('ratio', 1) < 0.8:
            violations.append({
                'type': 'Fairness Violation',
                'metric': 'demographic_parity',
                'value': metrics['fairness']['demographic_parity']['ratio'],
                'threshold': 0.8
            })
        
        # Performance degradation
        if metrics['performance']['accuracy'] < self.baseline['accuracy'] * 0.95:
            violations.append({
                'type': 'Performance Degradation',
                'metric': 'accuracy',
                'current': metrics['performance']['accuracy'],
                'baseline': self.baseline['accuracy']
            })
        
        return violations
```

## Best Practices

1. **Proactive Bias Detection:** Test for bias before deployment
2. **Multiple Fairness Metrics:** No single metric captures all fairness aspects
3. **Transparency by Design:** Build explainability into the system
4. **Privacy-First Approach:** Implement privacy protections from the start
5. **Continuous Monitoring:** Ethics is not a one-time check
6. **Stakeholder Involvement:** Include affected communities in design
7. **Documentation:** Maintain comprehensive documentation
8. **Regular Audits:** Schedule periodic ethics reviews
9. **Incident Response:** Have a plan for when things go wrong
10. **Trade-off Communication:** Be transparent about fairness-accuracy trade-offs