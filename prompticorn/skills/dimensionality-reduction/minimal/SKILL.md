# Dimensionality Reduction (Minimal)

## Purpose
Compress a wide feature space into fewer coordinates while keeping the structure that matters, and know what each method destroys in exchange.

## Core Techniques

### 1. Scale Before PCA
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

pipe = make_pipeline(StandardScaler(), PCA(n_components=0.95))
```
PCA maximizes variance. Income in dollars has variance ~10⁹; age in years ~10². Unscaled, the first component is income and nothing else — the method has simply found the largest measurement unit. `PCA` centres the data itself but does not standardize it.

### 2. Choose n_components From the Spectrum, Not a Round Number
```python
PCA(n_components=0.95)          # keep enough components for 95% variance
pca.explained_variance_ratio_.cumsum()
```
Plot the cumulative curve and look for the elbow. "95%" is a convention, not a law: if 40 of 500 components carry 95% of the variance you have found real redundancy; if it takes 480, your features are close to independent and PCA will not help.

### 3. Know What Each Method Preserves
| Method | Preserves | Use for | Transforms new data |
|---|---|---|---|
| PCA | Global variance, linear | Decorrelation, compression | Yes |
| TruncatedSVD | Same, no centring | Sparse matrices (TF-IDF) | Yes |
| t-SNE | Local neighbourhoods | 2-D visualization only | No |
| UMAP | Local + some global | Visualization, sometimes features | Yes |
| LDA | Class separability | Supervised, ≤ n_classes−1 dims | Yes |

t-SNE has no `transform` method — it cannot embed new points, so it can never be a preprocessing step in a serving pipeline.

### 4. PCA Components Are Not Interpretable Features
Each component is a dense linear combination of every original column. "PC1 = 0.31·age − 0.22·income + 0.19·tenure + …" has no business meaning, cannot be explained to a regulator, and breaks any feature-importance story. When interpretability is required, select features (see feature-engineering) rather than project them.

### 5. Do Not Over-Read t-SNE and UMAP Plots
Cluster sizes and inter-cluster distances in a t-SNE plot are largely artefacts of `perplexity` and the optimization, not properties of the data. Two well-separated blobs may be adjacent in the original space. Vary `perplexity` (5–50) and inspect several runs before believing any structure.

### 6. Fit Inside the Fold
PCA fitted on the full dataset has seen the validation rows' covariance. The leak is subtler than target leakage but real, and it inflates CV scores. Keep the reducer as a pipeline step.

## Warning Signs

- PCA applied to unstandardized features of mixed units
- `n_components` set to a round number with no variance check
- PCA components described as if they were meaningful variables
- t-SNE output used as model input, or its cluster distances read literally
- Dimensionality reduction applied before a tree model, which does not need it
- Reducer fitted before the train/test split
- Accuracy dropping noticeably after reduction with no compute benefit gained
