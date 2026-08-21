"""Chapter 20: Data Licences, Attribution, Privacy, and Reproducibility.

Standalone construction code: no creditriskbook imports.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetLicenceRecord:
    key: str
    publisher: str
    official_url: str
    licence: str
    redistribution: str
    attribution: str


def licence_gate(record: DatasetLicenceRecord) -> tuple[bool, tuple[str, ...]]:
    issues = []
    for field in ("publisher", "official_url", "licence", "redistribution", "attribution"):
        if not getattr(record, field).strip():
            issues.append(f"missing_{field}")
    if "unknown" in record.licence.lower():
        issues.append("licence_not_resolved")
    return not issues, tuple(issues)


approved = DatasetLicenceRecord(
    "uci_south_german",
    "UCI",
    "https://archive.ics.uci.edu/",
    "CC BY 4.0",
    "download by code",
    "UCI dataset and DOI",
)
blocked = DatasetLicenceRecord("mystery_csv", "", "", "unknown", "", "")
print("Approved record:", licence_gate(approved))
print("Blocked record:", licence_gate(blocked))
