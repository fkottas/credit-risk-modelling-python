## Mathematics-to-code laboratory — cleaning without hiding evidence

### 1. Specify every rule and disposition

Create a rule table with field, formula, population, severity, owner and action. Use the teaching conventions $0\le DPD\le999$, $0\le Balance\le1.20Limit$, non-negative payments, valid status, $snapshot\le reference$, and the documented DPD-status mapping. State which rules are product-specific.

### 2. Write scratch boolean masks

Start with `scratch_performance_rules` from the chapter. Return one boolean column per rule. Do not fill missing values, cap balances, coerce an unknown status or delete a row without an issue record.

### 3. Test ordinary, boundary and corrupted cases

Write expected results for DPD values $0,30,89,90,999,-1,1000$; balance exactly at 120% of limit; zero and negative payment; future snapshot; unparseable date; exact duplicate; and later correction. A later correction is retained only because the source contract declares processing-time precedence.

### 4. Promote and call the library

Move the tested rules into `creditriskbook.data.cleaning`, then call the promoted version:

```python
from creditriskbook.data import inject_behavioral_defects, make_behavioral_credit_history
from creditriskbook.data.cleaning import clean_monthly_performance

case = make_behavioral_credit_history(n_customers=200, months=18, seed=823)
dirty = inject_behavioral_defects(case.monthly_performance, seed=824)
refs = case.applications[["customer_id", "reference_date"]]
result = clean_monthly_performance(dirty, refs)
print(result.issues.groupby(["rule", "action"]).size())
assert len(result.clean) + len(result.quarantine) == len(dirty)
```

The output must contain row-level issue identifiers and a disposition. Re-run the rules on `result.clean`; critical failures must be zero.

### 5. Evidence pack

Submit raw checksum, dirty-copy seed, rule register, before/after profiles, row-count bridge, quarantine table, tests, exception ticket and a statement that the cleaner is prohibited from silently changing business values.
