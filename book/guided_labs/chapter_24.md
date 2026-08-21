## Mathematics-to-code laboratory — behavioural features from first principles

### 1. Compute one cured borrower by hand

Use monthly DPD $[60,30,0]$ and two contracts, one opened inside the six-month window. Before code, calculate `max_dpd_6m=60`, `last_dpd=0`, `count_dpd30_6m=2` and `count_contracts_last_6m=1`. Explain why maximum and last DPD must not be confused.

### 2. Implement the four core features

Write `scratch_core_features` exactly from the set definitions. Aggregate multiple contracts to one customer-month before DPD counts. Use the open-left, closed-right boundary $(t-6m,t]`. Return history length and missing history explicitly.

### 3. Extend the mathematics

Implement utilisation $U_s=\sum_j Balance_{j,s}/\sum_j Limit_{j,s}$, payment ratio, DPD threshold counts, recency and the closed-form OLS utilisation slope. Reconcile the slope against a sequence $[0.1,0.2,\ldots,0.6]$, whose slope per month is $0.1$.

### 4. Test point-in-time invariance

Append a future row with DPD 999, a future contract and a future enquiry. Every feature at the original reference date must be bitwise identical. Add two contracts delinquent in the same month and verify one delinquent month is counted. Test the exact six-month boundary.

### 5. Promote, call and evaluate rationality

After scratch tests pass, move the implementation into `creditriskbook.features.behavioral` and call it:

```python
from creditriskbook.features import build_behavioral_features

features = build_behavioral_features(
    clean_performance,
    contracts,
    reference_dates,
    enquiries=enquiries,
)
print(features[[
    "max_dpd_6m", "last_dpd", "count_dpd30_6m",
    "count_contracts_last_6m", "utilisation_slope_6m",
]].head())
```

Create characteristic tables by feature band with count, event count, event rate, confidence interval, missingness and time/segment split. Investigate direction; do not force monotonicity because the feature name sounds risky.

### 6. Evidence pack

Submit formulas, hand calculation, scratch code, unit tests, library diff, output table, characteristic analysis, point-in-time proof, limitations and prohibited-use statement. These features support a model; they are not policy rules by themselves.
