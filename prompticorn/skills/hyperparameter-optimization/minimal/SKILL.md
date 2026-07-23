# Hyperparameter Optimization (Minimal)

## Purpose
Search hyperparameter space efficiently, and get an honest estimate of how the tuned model will actually perform.

## Core Techniques

### 1. Prefer Random Search Over Grid Search
```python
from scipy.stats import loguniform, randint
from sklearn.model_selection import RandomizedSearchCV

search = RandomizedSearchCV(
    estimator=model,
    param_distributions={
        "learning_rate": loguniform(1e-3, 3e-1),   # sample in log space
        "max_depth": randint(3, 12),
        "subsample": loguniform(0.5, 1.0),
    },
    n_iter=60, cv=5, scoring="neg_log_loss",
    random_state=0, n_jobs=-1,
)
```
Grid search wastes budget: a 4×4×4×4 grid spends 256 fits but only tries 4 distinct values of the one parameter that matters. Bergstra & Bengio (2012) showed most spaces have low *effective* dimensionality — two or three parameters dominate — so random search, which gives every trial a fresh value for every parameter, covers those axes far better at equal cost. With 60 random draws you land in the top 5% region of the space with ~95% probability, regardless of dimension.

### 2. Sample Scale-Sensitive Parameters in Log Space
Learning rate, regularization strength, and `C` span orders of magnitude. Uniform sampling on `[1e-5, 1e-1]` puts 90% of draws above 0.01 and never probes the small end. Use `loguniform`, or `trial.suggest_float(..., log=True)`.

### 3. Use Bayesian Search When Fits Are Expensive
```python
import optuna

def objective(trial):
    params = {
        "learning_rate": trial.suggest_float("learning_rate", 1e-3, 3e-1, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_child_weight": trial.suggest_float("min_child_weight", 1e-2, 10.0, log=True),
    }
    return cross_val_score(make_model(**params), X, y, cv=5,
                           scoring="neg_log_loss").mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
```
TPE pays off when a single fit costs minutes and you have ~50+ trials. Below ~30 trials it has not seen enough to model the space and roughly matches random search.

### 4. Never Tune Against the Test Set
Every time you look at test performance and change a hyperparameter, you fit one bit of the test set. After 200 trials the best score is inflated by selection noise — you have chosen the configuration that got lucky on those particular rows. Split three ways (train / validation / test) and touch the test set once, at the end, or use nested CV:
```python
inner = KFold(5, shuffle=True, random_state=0)
outer = KFold(5, shuffle=True, random_state=1)
search = RandomizedSearchCV(model, dist, n_iter=40, cv=inner)
honest = cross_val_score(search, X, y, cv=outer)   # tuning happens inside each fold
```
The gap between `search.best_score_` and the outer score is your optimism — commonly 1–3 points on small data.

### 5. Prune Hopeless Trials Early
```python
study = optuna.create_study(pruner=optuna.pruners.MedianPruner(n_warmup_steps=5))
# inside the objective, per epoch:
trial.report(val_loss, step=epoch)
if trial.should_prune():
    raise optuna.TrialPruned()
```
Successive halving (`HalvingRandomSearchCV`) does the same for non-iterative models by giving each surviving config more data. Both buy 3–10× more configurations for the same wall clock.

### 6. Fix the Seed, Vary the Split
A config that wins by 0.2% on one 5-fold split is noise. Repeat the CV with different split seeds (`RepeatedStratifiedKFold`) before declaring a winner, and only tune what moves the metric — for gradient boosting that is usually learning rate, tree depth, and one regularization term.

## Warning Signs

- Test score reported from the same data used to pick hyperparameters
- Uniform (not log) ranges on learning rate or regularization strength
- Best value sitting on a boundary of the search range — the optimum is outside it
- Grid search over 5+ parameters
- Selecting between configs whose CV scores differ by less than the fold std
- Random split CV on time-ordered data (see time-series-preprocessing)
