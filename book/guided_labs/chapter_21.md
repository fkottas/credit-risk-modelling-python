## Mathematics-to-code laboratory — construct a point-in-time join

### 1. State the record-selection set

For decision $i$ at time $t_i$, eligible source rows satisfy $s\le t_i$. The selected row is $s_i^*=\max\{s:s\le t_i\}$. Write this expression, then calculate the selected record by hand for three customers: one normal match, one future-only match and one stale match.

### 2. Implement without a convenience join

Use a loop and boolean filter first. Return decision time, selected effective time, processing time, age in days and source row identifier. Do not import the project library in this step. Assert that selected effective time never exceeds decision time.

```python
def select_known_record(decisions, events):
    rows = []
    for decision in decisions.itertuples(index=False):
        known = events.loc[
            (events.customer_id == decision.customer_id)
            & (events.effective_time <= decision.decision_time)
            & (events.processing_time <= decision.decision_time)
        ].sort_values(["effective_time", "processing_time"])
        chosen = known.tail(1)
        rows.append((decision.customer_id, None if chosen.empty else chosen.index[0]))
    return rows
```

### 3. Test timing, duplicates and staleness

Add a future record containing an extreme risk value. The earlier result must not change. Add two processing versions for one effective date and select only the version known at decision time. Add a maximum-staleness rule and make the stale result missing rather than substituting a future record.

### 4. Promote and compare

After the tests pass, move the generic selection logic into the student's data module. Compare its output with `pandas.merge_asof` on the same sorted inputs. Reconcile row count and show that a naïve latest-record join fails the future-leakage test.

### 5. Evidence pack

Submit the formula, hand table, scratch function, tests, promoted module, reconciliation, lineage map and a prohibited-use statement. The join is a data-availability control; it is not authority to use the selected field for a credit decision.
