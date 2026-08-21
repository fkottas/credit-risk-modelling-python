"""Chapter 6: The Credit Model Operating System.

Standalone construction code: no creditriskbook imports.
"""

import hashlib
import json


def reproducible_run_id(data_hash: str, code_hash: str, policy: dict) -> str:
    """Hash canonical evidence; never hash an unordered string representation."""
    payload = {"data_hash": data_hash, "code_hash": code_hash, "policy": policy}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


policy = {"horizon_months": 12, "default_dpd": 90, "version": "1.0"}
run_id = reproducible_run_id("data-9f2a", "code-31bc", policy)
print("Run ID:", run_id)
print("Length:", len(run_id), "hexadecimal:", all(c in "0123456789abcdef" for c in run_id))
