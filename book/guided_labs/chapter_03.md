## Worked calculation — What changes when PD, LGD, and EAD deteriorate together?

Multiplying separately averaged parameters ignores dependence and can understate downturn loss.

**Companion case:** `synthetic_ifrs9_schedule`. **Implementation level:** From first principles: scalar values, lists, and the Python standard library; intermediate quantities remain visible.

### Method

The calculation follows

\[
\operatorname{Var}(L)=\sum_{i=1}^{n}\operatorname{Var}(L_i)+2\sum_{i=1}^{n-1}\sum_{j=i+1}^{n}\operatorname{Cov}(L_i,L_j)
\]


### Python implementation

```python
scenarios = [
    # name, weight, PD, LGD, EAD
    ("base", 0.60, 0.03, 0.35, 10_000.0),
    ("downturn", 0.25, 0.09, 0.50, 11_000.0),
    ("severe", 0.15, 0.20, 0.65, 12_000.0),
]

coherent_el = 0.0
average_pd = average_lgd = average_ead = 0.0
for name, weight, pd, lgd, ead in scenarios:
    scenario_el = pd * lgd * ead
    coherent_el += weight * scenario_el
    average_pd += weight * pd
    average_lgd += weight * lgd
    average_ead += weight * ead
    print(name, "EL=", round(scenario_el, 2), "weighted EL=", round(weight * scenario_el, 2))

product_of_averages = average_pd * average_lgd * average_ead
print("Weighted scenario EL:", round(coherent_el, 2))
print("Product of separate averages:", round(product_of_averages, 2))
print("Dependence effect:", round(coherent_el - product_of_averages, 2))
```

### Executed result

```output
base EL= 105.0 weighted EL= 63.0
downturn EL= 495.0 weighted EL= 123.75
severe EL= 1560.0 weighted EL= 234.0
Weighted scenario EL: 420.75
Product of separate averages: 321.68
Dependence effect: 99.07
```

### Interpretation

The severe scenario has the smallest weight but the largest weighted contribution because PD, LGD and EAD deteriorate together. Separate averages would conceal that joint movement.

**Validation:** Compare account-level scenario aggregation with the product of separately averaged components.

### Exercises

1. Repeat the calculation with **the synthetic retail and synthetic IFRS 9 scenario datasets** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
