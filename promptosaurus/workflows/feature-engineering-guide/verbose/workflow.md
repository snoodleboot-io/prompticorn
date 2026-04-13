---
name: feature-engineering-guide
description: "Transform raw data into meaningful features for ML models"
agent: "mlai"
category: "ml"
related_workflows:
  - data-quality-monitoring
  - model-evaluation-workflow
  - experiment-tracking-setup
---

# Feature Engineering Guide - Comprehensive Guide

## Problem Context

Feature engineering is the process of transforming raw data into features that better represent the underlying problem to predictive models. Good feature engineering can significantly improve model performance, reduce training time, and make models more interpretable. This workflow provides a systematic approach to creating, selecting, and validating features for machine learning models.

## Prerequisites

- Raw dataset available for analysis
- Understanding of the business problem and domain
- Python environment with data science libraries
- Knowledge of the target variable and prediction task
- Access to domain experts for feature validation

## Step-by-Step Implementation

### Step 1: Exploratory Data Analysis

#### 1.1 Load and Inspect Data
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load data
df = pd.read_csv('raw_data.csv')

# Basic inspection
print(f"Dataset shape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nBasic statistics:\n{df.describe()}")

# Check for duplicates
duplicates = df.duplicated().sum()
print(f"\nDuplicate rows: {duplicates}")
```

#### 1.2 Analyze Distributions
```python
# Numerical features distribution
numerical_features = df.select_dtypes(include=['float64', 'int64']).columns

fig, axes = plt.subplots(len(numerical_features), 2, figsize=(12, 4*len(numerical_features)))

for idx, col in enumerate(numerical_features):
    # Histogram
    axes[idx, 0].hist(df[col].dropna(), bins=30, edgecolor='black')
    axes[idx, 0].set_title(f'{col} - Distribution')
    
    # Box plot
    axes[idx, 1].boxplot(df[col].dropna())
    axes[idx, 1].set_title(f'{col} - Outliers')

plt.tight_layout()
plt.show()

# Check for skewness
for col in numerical_features:
    skewness = df[col].skew()
    if abs(skewness) > 1:
        print(f"{col}: Highly skewed (skewness = {skewness:.2f})")
```

### Step 2: Handle Missing Values

#### 2.1 Analyze Missing Patterns
```python
import missingno as msno

# Visualize missing patterns
msno.matrix(df)
plt.show()

# Missing value heatmap
msno.heatmap(df)
plt.show()

# Analyze missing mechanisms
def analyze_missing_mechanism(df, target_col):
    """Determine if missing is random or systematic."""
    
    for col in df.columns:
        if df[col].isnull().any():
            # Create indicator for missing
            df[f'{col}_missing'] = df[col].isnull().astype(int)
            
            # Check correlation with target
            if target_col in df.columns:
                corr = df[f'{col}_missing'].corr(df[target_col])
                if abs(corr) > 0.1:
                    print(f"{col}: Missing may be informative (corr={corr:.3f})")
```

#### 2.2 Imputation Strategies
```python
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

class SmartImputer:
    def __init__(self, strategy='auto'):
        self.strategy = strategy
        self.imputers = {}
        
    def fit_transform(self, df):
        df_imputed = df.copy()
        
        for col in df.columns:
            if df[col].isnull().any():
                missing_pct = df[col].isnull().sum() / len(df)
                
                if missing_pct > 0.5:
                    # Too much missing - create indicator and drop
                    df_imputed[f'{col}_was_missing'] = df[col].isnull().astype(int)
                    df_imputed = df_imputed.drop(col, axis=1)
                    
                elif df[col].dtype in ['float64', 'int64']:
                    if missing_pct < 0.05:
                        # Little missing - use median
                        imputer = SimpleImputer(strategy='median')
                    else:
                        # Moderate missing - use KNN
                        imputer = KNNImputer(n_neighbors=5)
                    
                    df_imputed[col] = imputer.fit_transform(df[[col]])
                    self.imputers[col] = imputer
                    
                else:
                    # Categorical - use mode
                    mode = df[col].mode()[0] if not df[col].mode().empty else 'missing'
                    df_imputed[col].fillna(mode, inplace=True)
        
        return df_imputed

# Apply smart imputation
imputer = SmartImputer()
df_imputed = imputer.fit_transform(df)
```

### Step 3: Encode Categorical Variables

#### 3.1 Encoding Strategies
```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from category_encoders import TargetEncoder, BinaryEncoder, HashingEncoder

class CategoricalEncoder:
    def __init__(self, target=None):
        self.encoders = {}
        self.target = target
        
    def fit_transform(self, df):
        df_encoded = df.copy()
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            unique_values = df[col].nunique()
            
            if unique_values == 2:
                # Binary encoding for 2 categories
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df[col])
                self.encoders[col] = ('label', le)
                
            elif unique_values < 10:
                # One-hot for low cardinality
                df_encoded = pd.get_dummies(df_encoded, columns=[col], prefix=col)
                self.encoders[col] = ('onehot', None)
                
            elif unique_values < 50 and self.target is not None:
                # Target encoding for medium cardinality
                te = TargetEncoder()
                df_encoded[col] = te.fit_transform(df[col], df[self.target])
                self.encoders[col] = ('target', te)
                
            else:
                # Hashing for high cardinality
                he = HashingEncoder(n_components=10)
                hashed = he.fit_transform(df[[col]])
                df_encoded = pd.concat([df_encoded.drop(col, axis=1), hashed], axis=1)
                self.encoders[col] = ('hashing', he)
        
        return df_encoded

# Apply encoding
encoder = CategoricalEncoder(target='target_column')
df_encoded = encoder.fit_transform(df_imputed)
```

### Step 4: Feature Scaling

#### 4.1 Scaling Strategies
```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, QuantileTransformer

class AdaptiveScaler:
    def __init__(self):
        self.scalers = {}
        
    def fit_transform(self, df):
        df_scaled = df.copy()
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        
        for col in numerical_cols:
            # Check distribution characteristics
            skewness = abs(df[col].skew())
            outlier_pct = len(df[(df[col] < df[col].quantile(0.01)) | 
                                (df[col] > df[col].quantile(0.99))]) / len(df)
            
            if outlier_pct > 0.1:
                # Many outliers - use RobustScaler
                scaler = RobustScaler()
            elif skewness > 2:
                # Highly skewed - use QuantileTransformer
                scaler = QuantileTransformer(output_distribution='normal')
            elif df[col].min() >= 0 and df[col].max() <= 1:
                # Already in [0,1] range - skip
                continue
            else:
                # Standard case - use StandardScaler
                scaler = StandardScaler()
            
            df_scaled[col] = scaler.fit_transform(df[[col]])
            self.scalers[col] = scaler
        
        return df_scaled

# Apply scaling
scaler = AdaptiveScaler()
df_scaled = scaler.fit_transform(df_encoded)
```

### Step 5: Feature Creation

#### 5.1 Polynomial and Interaction Features
```python
from sklearn.preprocessing import PolynomialFeatures
from itertools import combinations

def create_polynomial_features(df, degree=2, include_cols=None):
    """Create polynomial features for specified columns."""
    
    if include_cols is None:
        include_cols = df.select_dtypes(include=['float64', 'int64']).columns[:5]
    
    poly = PolynomialFeatures(degree=degree, include_bias=False)
    poly_features = poly.fit_transform(df[include_cols])
    
    # Get feature names
    feature_names = poly.get_feature_names_out(include_cols)
    
    # Create DataFrame
    poly_df = pd.DataFrame(poly_features, columns=feature_names, index=df.index)
    
    # Remove original features (already in df)
    poly_df = poly_df.drop(columns=include_cols)
    
    return pd.concat([df, poly_df], axis=1)

def create_interaction_features(df, cols_pairs):
    """Create interaction features for specified column pairs."""
    
    df_interactions = df.copy()
    
    for col1, col2 in cols_pairs:
        # Multiplication
        df_interactions[f'{col1}_times_{col2}'] = df[col1] * df[col2]
        
        # Division (with protection against division by zero)
        df_interactions[f'{col1}_div_{col2}'] = df[col1] / (df[col2] + 1e-8)
        
        # Difference
        df_interactions[f'{col1}_minus_{col2}'] = df[col1] - df[col2]
        
        # Sum
        df_interactions[f'{col1}_plus_{col2}'] = df[col1] + df[col2]
    
    return df_interactions

# Create features
df_poly = create_polynomial_features(df_scaled, degree=2)

# Define meaningful interactions based on domain knowledge
interaction_pairs = [('feature1', 'feature2'), ('feature3', 'feature4')]
df_features = create_interaction_features(df_poly, interaction_pairs)
```

#### 5.2 Domain-Specific Features
```python
def create_domain_features(df, domain='retail'):
    """Create domain-specific features."""
    
    df_domain = df.copy()
    
    if domain == 'retail':
        # Retail-specific features
        if 'price' in df.columns and 'quantity' in df.columns:
            df_domain['total_value'] = df['price'] * df['quantity']
        
        if 'date' in df.columns:
            df_domain['date'] = pd.to_datetime(df['date'])
            df_domain['day_of_week'] = df_domain['date'].dt.dayofweek
            df_domain['is_weekend'] = df_domain['day_of_week'].isin([5, 6]).astype(int)
            df_domain['month'] = df_domain['date'].dt.month
            df_domain['quarter'] = df_domain['date'].dt.quarter
            df_domain['is_holiday'] = check_holiday(df_domain['date'])
    
    elif domain == 'finance':
        # Finance-specific features
        if 'income' in df.columns and 'debt' in df.columns:
            df_domain['debt_to_income'] = df['debt'] / (df['income'] + 1)
        
        if 'credit_score' in df.columns:
            df_domain['credit_category'] = pd.cut(
                df['credit_score'], 
                bins=[0, 580, 670, 740, 800, 850],
                labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
            )
    
    return df_domain

# Apply domain features
df_final = create_domain_features(df_features, domain='retail')
```

### Step 6: Feature Selection

#### 6.1 Statistical Feature Selection
```python
from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

class FeatureSelector:
    def __init__(self, target, task='classification'):
        self.target = target
        self.task = task
        self.selected_features = []
        
    def select_features(self, df, methods=['statistical', 'rfe', 'importance'], k=50):
        """Select top k features using multiple methods."""
        
        X = df.drop(columns=[self.target])
        y = df[self.target]
        
        scores = {}
        
        if 'statistical' in methods:
            # Statistical tests
            if self.task == 'classification':
                selector = SelectKBest(f_classif, k=k)
            else:
                selector = SelectKBest(f_regression, k=k)
            
            selector.fit(X, y)
            scores['statistical'] = dict(zip(X.columns, selector.scores_))
        
        if 'rfe' in methods:
            # Recursive Feature Elimination
            estimator = RandomForestClassifier(n_estimators=50, random_state=42)
            rfe = RFE(estimator, n_features_to_select=k)
            rfe.fit(X, y)
            scores['rfe'] = dict(zip(X.columns, rfe.ranking_))
        
        if 'importance' in methods:
            # Feature importance from Random Forest
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X, y)
            scores['importance'] = dict(zip(X.columns, rf.feature_importances_))
        
        # Combine scores
        combined_scores = {}
        for col in X.columns:
            combined_scores[col] = sum(
                scores[method].get(col, 0) for method in scores
            )
        
        # Select top k features
        self.selected_features = sorted(
            combined_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:k]
        
        return [f[0] for f in self.selected_features]

# Apply feature selection
selector = FeatureSelector(target='target_column', task='classification')
selected_features = selector.select_features(df_final, k=30)

df_selected = df_final[selected_features + ['target_column']]
```

### Step 7: Feature Validation

#### 7.1 Cross-Validation Pipeline
```python
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

def validate_features(df, target, cv=5):
    """Validate feature engineering pipeline."""
    
    X = df.drop(columns=[target])
    y = df[target]
    
    # Create pipeline
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Cross-validation
    scores = cross_val_score(pipeline, X, y, cv=cv, scoring='accuracy')
    
    print(f"Cross-validation scores: {scores}")
    print(f"Mean accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
    
    return scores

# Validate features
validation_scores = validate_features(df_selected, 'target_column')
```

#### 7.2 Save Feature Pipeline
```python
import joblib
import json

class FeatureEngineeringPipeline:
    def __init__(self, imputer, encoder, scaler, selector, selected_features):
        self.imputer = imputer
        self.encoder = encoder
        self.scaler = scaler
        self.selector = selector
        self.selected_features = selected_features
        
    def transform(self, df):
        """Apply full feature engineering pipeline."""
        
        df_transformed = self.imputer.transform(df)
        df_transformed = self.encoder.transform(df_transformed)
        df_transformed = self.scaler.transform(df_transformed)
        df_transformed = df_transformed[self.selected_features]
        
        return df_transformed
    
    def save(self, path):
        """Save pipeline to disk."""
        
        joblib.dump(self, f'{path}/feature_pipeline.pkl')
        
        # Save metadata
        metadata = {
            'selected_features': self.selected_features,
            'n_features': len(self.selected_features),
            'created_at': pd.Timestamp.now().isoformat()
        }
        
        with open(f'{path}/feature_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

# Create and save pipeline
pipeline = FeatureEngineeringPipeline(
    imputer=imputer,
    encoder=encoder,
    scaler=scaler,
    selector=selector,
    selected_features=selected_features
)

pipeline.save('models/')
```

## Best Practices

1. **Prevent Data Leakage:** Always split data before feature engineering
2. **Handle Missing Values:** Don't drop rows unless absolutely necessary
3. **Encode Wisely:** Choose encoding based on cardinality and relationship with target
4. **Scale Appropriately:** Consider distribution and algorithm requirements
5. **Create Meaningful Features:** Use domain knowledge to guide feature creation
6. **Validate Thoroughly:** Test pipeline on holdout data

## Anti-Patterns to Avoid

1. **Using Test Data:** Never use test data for any feature engineering decisions
2. **Over-Engineering:** Don't create hundreds of features without validation
3. **Ignoring Domain Knowledge:** Always incorporate business understanding
4. **One-Size-Fits-All:** Different models need different feature engineering
5. **Not Versioning:** Always version your feature engineering pipeline

## Integration Points

- **Data Pipeline:** Connect to data ingestion and cleaning processes
- **Model Training:** Feed engineered features to training pipeline
- **Feature Store:** Save features for reuse across models
- **Monitoring:** Track feature distributions in production

## Troubleshooting

### Issue: High dimensionality after encoding
**Solution:** Use dimensionality reduction or more aggressive feature selection

### Issue: Model performance doesn't improve
**Solution:** Review feature importance, try different engineering strategies

### Issue: Pipeline fails on new data
**Solution:** Add robust error handling, validate input schema

## Related Workflows

- [Data Quality Monitoring](../data-quality-monitoring) for ensuring data quality
- [Model Evaluation Workflow](../model-evaluation-workflow) for validating feature impact
- [Experiment Tracking Setup](../experiment-tracking-setup) for tracking feature experiments