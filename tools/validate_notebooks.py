"""Parse and execute every notebook without requiring Jupyter."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("nbformat") != 4 or not isinstance(data.get("cells"), list):
        raise ValueError(f"{path}: expected nbformat 4 and a cells list")
    code_cells = []
    for index, cell in enumerate(data["cells"]):
        if cell.get("cell_type") not in {"markdown", "code", "raw"} or "source" not in cell:
            raise ValueError(f"{path}: invalid cell {index}")
        if cell["cell_type"] == "code":
            source = cell["source"]
            code_cells.append("".join(source) if isinstance(source, list) else str(source))
    script = "\n\n".join(f"# cell {i + 1}\n{source}" for i, source in enumerate(code_cells))
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as handle:
        handle.write(script)
        temporary = Path(handle.name)
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + environment.get("PYTHONPATH", "")
    environment["MPLBACKEND"] = "Agg"
    environment["MPLCONFIGDIR"] = str(Path(tempfile.gettempdir()) / "creditriskbook-matplotlib")
    try:
        completed = subprocess.run(
            [sys.executable, str(temporary)],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            timeout=180,
        )
    finally:
        temporary.unlink(missing_ok=True)
    if completed.returncode:
        raise RuntimeError(
            f"{path} failed with exit code {completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    print(f"PASS {path.relative_to(ROOT)} ({len(code_cells)} code cells)")


def main() -> None:
    notebooks = sorted((ROOT / "notebooks").rglob("*.ipynb"))
    if not notebooks:
        raise RuntimeError("No notebooks found")
    for path in notebooks:
        validate(path)
    print(f"Validated and executed {len(notebooks)} notebooks")


if __name__ == "__main__":
    main()
