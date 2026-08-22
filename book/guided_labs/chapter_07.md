## Worked calculation — Why do product contracts create different risk measures?

Amortising loans, cards, and mortgages generate different exposure paths, prepayment behaviour, and relevant features.

**Companion case:** `synthetic_retail`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
EAD_t=B_t+CCF_t(L_t-B_t)
\]


![Figure 7.1 — Observed default rates across the project-generated product cases.](book/figures/part-02-product-risk.png)

### Python implementation

```python
import pandas as pd


def product_exposure(product: str, drawn: float, limit: float, ccf: float) -> float:
    if drawn < 0 or limit < drawn or not 0 <= ccf <= 1:
        raise ValueError("Invalid drawn amount, limit, or CCF")
    if product in {"credit_card", "overdraft"}:
        return drawn + ccf * (limit - drawn)
    return drawn


facilities = pd.DataFrame({
    "product": ["term_loan", "credit_card", "overdraft"],
    "drawn": [18_000.0, 2_000.0, 7_000.0], "limit": [18_000.0, 8_000.0, 10_000.0],
    "ccf": [0.0, 0.65, 0.40],
})
facilities["ead"] = [product_exposure(*row) for row in facilities.itertuples(index=False, name=None)]
print(facilities.to_string(index=False))
```

### Executed result

```output
product   drawn   limit  ccf     ead
  term_loan 18000.0 18000.0 0.00 18000.0
credit_card  2000.0  8000.0 0.65  5900.0
  overdraft  7000.0 10000.0 0.40  8200.0
```

### Interpretation

The term loan has no undrawn component, whereas the card's 0.65 conversion factor raises EAD from EUR 2,000 drawn to EUR 5,900. Product terms determine the exposure calculation.

**Validation:** Reconcile balances, limits, and cash-flow timing under each product definition.

### Exercises

1. Repeat the calculation with **synthetic retail products and the Taiwan credit-card data** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
