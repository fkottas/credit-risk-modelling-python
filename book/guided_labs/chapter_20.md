## Worked calculation — What permissions and attribution are required before data are downloaded or redistributed?

Public access describes availability, not necessarily the permitted use of raw or derived data.

**Companion case:** `dataset_registry.yml`. **Implementation level:** From first principles: the calculation is written in full; NumPy or pandas is used only for transparent array and table operations.

### Method

The calculation follows

\[
\text{reproducible}=\mathbf{1}\{hash(data)=h_d,\;hash(code)=h_c\}
\]


![Figure 20.1 — Source terms and analytical suitability determine whether data are bundled, downloaded, or excluded.](book/figures/dataset-licence-decision-gate.png)

### Python implementation

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetLicenceRecord:
    key: str
    publisher: str
    official_url: str
    licence: str
    redistribution: str
    attribution: str


def review_licence_record(record: DatasetLicenceRecord) -> tuple[bool, tuple[str, ...]]:
    issues = []
    for field in ("publisher", "official_url", "licence", "redistribution", "attribution"):
        if not getattr(record, field).strip():
            issues.append(f"missing_{field}")
    if "unknown" in record.licence.lower():
        issues.append("licence_not_resolved")
    return not issues, tuple(issues)


approved = DatasetLicenceRecord("uci_south_german", "UCI", "https://archive.ics.uci.edu/",
                                "CC BY 4.0", "download by code", "UCI dataset and DOI")
blocked = DatasetLicenceRecord("mystery_csv", "", "", "unknown", "", "")
print("Approved record:", review_licence_record(approved))
print("Blocked record:", review_licence_record(blocked))
```

### Executed result

```output
Approved record: (True, ())
Blocked record: (False, ('missing_publisher', 'missing_official_url', 'missing_redistribution', 'missing_attribution', 'licence_not_resolved'))
```

### Interpretation

The complete licence record passes, while the incomplete record fails for five named reasons. Access is blocked until source, permission, redistribution and attribution are resolved.

**Validation:** Verify publisher, current terms, attribution, redistribution, checksum, and access date.

### Exercises

1. Repeat the calculation with **South German Credit and a conditional Kaggle source** and document any difference in population, observation unit, outcome, information date, horizon, or permitted use.
2. Change one assumption that appears in the equation. Predict the direction of the result before execution, then explain the observed sensitivity.
3. Complete the stated validation and identify one conclusion that the available evidence does not support.
