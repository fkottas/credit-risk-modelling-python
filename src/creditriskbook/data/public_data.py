"""Narrow, auditable adapters for public macroeconomic and complaint data.

These adapters do not convert macroeconomic observations or complaints into credit
outcomes. They preserve the publisher's meaning and attach source and use limits to
the returned table.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PublicDataBundle:
    key: str
    frame: pd.DataFrame
    source_url: str
    licence: str
    attribution: str
    accessed_on: str
    limitations: str


def load_world_bank_wdi(
    countries: tuple[str, ...],
    indicators: tuple[str, ...],
    *,
    start_year: int,
    end_year: int,
    timeout: int = 60,
    opener: Callable[..., object] | None = None,
) -> PublicDataBundle:
    """Retrieve a small World Development Indicators panel from the official API."""

    if not countries or not indicators:
        raise ValueError("At least one country and one indicator are required")
    if not 1960 <= start_year <= end_year <= date.today().year:
        raise ValueError("Use a valid closed year range between 1960 and the current year")
    country_codes = tuple(code.upper() for code in countries)
    indicator_codes = tuple(code.upper() for code in indicators)
    if any(not re.fullmatch(r"[A-Z]{2,3}", code) for code in country_codes):
        raise ValueError("Country codes must contain two or three ASCII letters")
    if any(not re.fullmatch(r"[A-Z0-9.]+", code) for code in indicator_codes):
        raise ValueError("Indicator codes may contain only letters, numbers and periods")

    path = (
        "https://api.worldbank.org/v2/country/"
        f"{';'.join(country_codes)}/indicator/{';'.join(indicator_codes)}"
    )
    query = urllib.parse.urlencode(
        {
            "source": "2",
            "format": "json",
            "date": f"{start_year}:{end_year}",
            "per_page": "20000",
        },
        safe=":;",
    )
    url = f"{path}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "creditriskbook/0.1"})
    open_url = opener or urllib.request.urlopen
    with open_url(request, timeout=timeout) as response:  # noqa: S310 - validated official host
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[1], list):
        raise ValueError("Unexpected response structure from the World Bank API")
    metadata, observations = payload
    rows = []
    for observation in observations:
        rows.append(
            {
                "country_code": observation.get("countryiso3code"),
                "country": observation.get("country", {}).get("value"),
                "year": int(observation["date"]),
                "indicator_code": observation.get("indicator", {}).get("id"),
                "indicator": observation.get("indicator", {}).get("value"),
                "value": observation.get("value"),
                "unit": observation.get("unit", ""),
                "observation_status": observation.get("obs_status", ""),
            }
        )
    frame = pd.DataFrame(rows).sort_values(
        ["country_code", "indicator_code", "year"], ignore_index=True
    )
    if frame.empty:
        raise ValueError("The requested WDI panel contains no observations")
    return PublicDataBundle(
        key="world_bank_wdi",
        frame=frame,
        source_url=url,
        licence="CC BY 4.0",
        attribution=(
            "World Bank, World Development Indicators; values retrieved through the Indicators API."
        ),
        accessed_on=str(date.today()),
        limitations=(
            "Country-level annual indicators are revised and are not borrower outcomes. "
            f"The API reported last update {metadata.get('lastupdated', 'unknown')}. "
            "Record the extraction date and do not treat a supervisory or constructed path as a forecast."
        ),
    )


def load_cfpb_complaint_extract(
    path: str | Path,
    *,
    include_narratives: bool = False,
) -> PublicDataBundle:
    """Validate a user-downloaded CFPB complaint CSV or CSV-in-ZIP extract.

    Narratives are excluded by default. Complaints are not a representative sample
    of customers and do not provide default, approval or causal-treatment outcomes.
    """

    source_path = Path(path)
    if not source_path.exists():
        raise FileNotFoundError(f"Complaint extract not found: {source_path}")
    frame = pd.read_csv(source_path, low_memory=False)
    required = {
        "Date received",
        "Product",
        "Issue",
        "Company",
        "State",
        "Submitted via",
        "Company response to consumer",
        "Timely response?",
        "Complaint ID",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"The complaint extract is missing fields: {sorted(missing)}")
    narrative = "Consumer complaint narrative"
    if not include_narratives and narrative in frame:
        frame = frame.drop(columns=[narrative])
    frame["Date received"] = pd.to_datetime(frame["Date received"], errors="coerce")
    if frame["Date received"].isna().any():
        raise ValueError("At least one complaint has an invalid received date")
    if frame["Complaint ID"].duplicated().any():
        raise ValueError("Complaint ID must be unique in the supplied extract")
    return PublicDataBundle(
        key="cfpb_consumer_complaints",
        frame=frame,
        source_url="https://www.consumerfinance.gov/data-research/consumer-complaints/",
        licence="Published complaint data are freely available for use, analysis and reuse",
        attribution="Consumer Financial Protection Bureau, Consumer Complaint Database.",
        accessed_on=str(date.today()),
        limitations=(
            "Published complaints are not a statistical sample and do not provide underwriting or "
            "default labels. Narratives are consumer statements, are not verified by the CFPB, and "
            "require additional privacy and text-governance review even after publication."
        ),
    )
