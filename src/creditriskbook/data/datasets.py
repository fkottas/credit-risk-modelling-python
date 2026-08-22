"""Legally reviewed dataset adapters with a common modelling contract."""

from __future__ import annotations

import hashlib
import io
import re
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.io import arff

from .synthetic import make_synthetic_retail_portfolio


@dataclass(frozen=True)
class QualitySpec:
    ranges: dict[str, tuple[float | None, float | None]] = field(default_factory=dict)
    allowed_values: dict[str, frozenset[Any]] = field(default_factory=dict)
    forbidden_model_columns: frozenset[str] = frozenset()


@dataclass(frozen=True)
class DatasetBundle:
    key: str
    frame: pd.DataFrame
    target: str
    numeric_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    protected_attributes: tuple[str, ...]
    id_column: str
    date_column: str | None
    split_strategy: str
    source_url: str
    licence: str
    attribution: str
    source_sha256: str
    limitations: str
    quality_spec: QualitySpec = QualitySpec()

    @property
    def model_features(self) -> tuple[str, ...]:
        return self.numeric_features + self.categorical_features


SOUTH_GERMAN_URL = "https://archive.ics.uci.edu/static/public/522/south+german+credit.zip"
SOUTH_GERMAN_ZIP_SHA256 = "0b40d40eb7321693d559e247a556f88a6cc8df8489c3cb2ae084db7592584551"
TAIWAN_URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
TAIWAN_ZIP_SHA256 = "56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602"
CREDIT_APPROVAL_URL = "https://archive.ics.uci.edu/static/public/27/credit+approval.zip"
CREDIT_APPROVAL_ZIP_SHA256 = "e3adfa0387815e3a9d8aaaf7b1cd7365424c83298bca6358bc48e451b4a26dd3"
AUSTRALIAN_APPROVAL_URL = (
    "https://archive.ics.uci.edu/static/public/143/statlog+australian+credit+approval.zip"
)
AUSTRALIAN_APPROVAL_ZIP_SHA256 = "f0bd9cd9b1d133cb20456b8953e1f8139fd30ed2b3f66da540db75136f1e9e0b"
POLISH_BANKRUPTCY_URL = (
    "https://archive.ics.uci.edu/static/public/365/polish+companies+bankruptcy+data.zip"
)
POLISH_BANKRUPTCY_ZIP_SHA256 = "17377929aa0b204bbf957e56462cf827c19fe4e2ce89f27dfbc77f9ea2bb16c9"
TAIWAN_BANKRUPTCY_URL = (
    "https://archive.ics.uci.edu/static/public/572/taiwanese+bankruptcy+prediction.zip"
)
TAIWAN_BANKRUPTCY_ZIP_SHA256 = "c346f5ad2618cb198e7ed8306cf2f31fe3bb2ec60acdbbe1736788d50f269aac"
STATLOG_GERMAN_URL = (
    "https://archive.ics.uci.edu/static/public/144/statlog%2Bgerman%2Bcredit%2Bdata.zip"
)
STATLOG_GERMAN_ZIP_SHA256 = "e12d9d5def6845c0622634a1cd2ab87fa470668c4298f1ec52a4e403376a435b"
BANK_MARKETING_URL = "https://archive.ics.uci.edu/static/public/222/bank%2Bmarketing.zip"
BANK_MARKETING_ZIP_SHA256 = "e0bf5f5de5b846e2f18e9d90606637267d46dfa260e0f17bb12e605db5efbeb4"


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _download_checked(url: str, expected_sha256: str, cache_path: Path, timeout: int = 60) -> bytes:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    if cache_path.exists():
        content = cache_path.read_bytes()
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "creditriskbook/0.1"})
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed reviewed URLs
            content = response.read()
        cache_path.write_bytes(content)
    observed = _sha256_bytes(content)
    if observed != expected_sha256:
        raise ValueError(
            f"Checksum mismatch for {url}. Expected {expected_sha256}, observed {observed}. "
            "The publisher may have changed the file; review it before updating the registry."
        )
    return content


def _normalise_name(value: object) -> str:
    name = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    return name


def _synthetic_bundle(n_rows: int, seed: int) -> DatasetBundle:
    frame = make_synthetic_retail_portfolio(n_rows=n_rows, seed=seed)
    content_hash = hashlib.sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()
    return DatasetBundle(
        key="synthetic_retail",
        frame=frame,
        target="default_12m",
        numeric_features=(
            "income",
            "employment_years",
            "debt_to_income",
            "utilisation",
            "credit_history_years",
            "enquiries_6m",
            "loan_amount",
            "term_months",
            "macro_unemployment",
        ),
        categorical_features=("region", "product", "home_ownership", "purpose"),
        protected_attributes=("age", "sex"),
        id_column="application_id",
        date_column="application_date",
        split_strategy="out_of_time",
        source_url="project-generated://synthetic_retail",
        licence="Project-generated synthetic teaching data",
        attribution="CreditRiskBook Synthetic Retail Portfolio, generated locally.",
        source_sha256=content_hash,
        limitations="Synthetic relationships are pedagogical and do not represent a real lender.",
        quality_spec=QualitySpec(
            ranges={
                "income": (0.0, None),
                "debt_to_income": (0.0, 1.5),
                "utilisation": (0.0, 1.0),
                "employment_years": (0.0, 65.0),
                "loan_amount": (0.0, None),
                "term_months": (1.0, 120.0),
            },
            allowed_values={
                "product": frozenset({"personal_loan", "credit_card", "bnpl"}),
                "home_ownership": frozenset({"rent", "mortgage", "own", "other"}),
            },
            forbidden_model_columns=frozenset(
                {"days_past_due_after_12m", "lgd", "ead", "interest_rate", "target_derived_score"}
            ),
        ),
    )


def _south_german_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        SOUTH_GERMAN_URL,
        SOUTH_GERMAN_ZIP_SHA256,
        cache_dir / "uci_south_german" / "south_german_credit.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("SouthGermanCredit.asc")
    frame = pd.read_csv(io.BytesIO(raw), sep=r"\s+")
    rename = {
        "laufkont": "status",
        "laufzeit": "duration",
        "moral": "credit_history",
        "verw": "purpose",
        "hoehe": "amount",
        "sparkont": "savings",
        "beszeit": "employment_duration",
        "rate": "installment_rate",
        "famges": "personal_status_sex",
        "buerge": "other_debtors",
        "wohnzeit": "present_residence",
        "verm": "property",
        "alter": "age",
        "weitkred": "other_installment_plans",
        "wohn": "housing",
        "bishkred": "number_credits",
        "beruf": "job",
        "pers": "people_liable",
        "telef": "telephone",
        "gastarb": "foreign_worker",
        "kredit": "credit_risk",
    }
    frame = frame.rename(columns=rename)
    frame.insert(0, "application_id", [f"SGC-{i:04d}" for i in range(len(frame))])
    frame["default_12m"] = (frame.pop("credit_risk") == 0).astype(int)
    numeric = ("duration", "amount")
    protected = ("age", "personal_status_sex", "foreign_worker")
    excluded = {"application_id", "default_12m", *numeric, *protected}
    categorical = tuple(column for column in frame.columns if column not in excluded)
    return DatasetBundle(
        key="uci_south_german",
        frame=frame,
        target="default_12m",
        numeric_features=numeric,
        categorical_features=categorical,
        protected_attributes=protected,
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/522/south+german+credit",
        licence="CC BY 4.0",
        attribution="South German Credit (2019), UCI ML Repository, DOI 10.24432/C5X89F.",
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "1973-1975 sample; bad credits were oversampled; amounts were transformed; "
            "no application dates are available for out-of-time testing."
        ),
        quality_spec=QualitySpec(
            ranges={"duration": (1.0, 120.0), "amount": (0.0, None)},
            allowed_values={
                column: frozenset(frame[column].dropna().unique()) for column in categorical
            },
            forbidden_model_columns=frozenset({"age", "personal_status_sex", "foreign_worker"}),
        ),
    )


def _statlog_german_bundle(cache_dir: Path) -> DatasetBundle:
    """Load the legacy German record for source-validation exercises.

    UCI's South German Credit documentation identifies serious coding-information
    problems in this older version. It is therefore exposed as a comparison source,
    not as the preferred German-credit benchmark.
    """

    archive = _download_checked(
        STATLOG_GERMAN_URL,
        STATLOG_GERMAN_ZIP_SHA256,
        cache_dir / "uci_statlog_german" / "statlog_german.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("german.data")
    columns = [f"a{i}" for i in range(1, 21)] + ["credit_risk"]
    frame = pd.read_csv(io.BytesIO(raw), sep=r"\s+", names=columns)
    frame.insert(0, "application_id", [f"GCR-{i:04d}" for i in range(len(frame))])
    frame["default_12m"] = (frame.pop("credit_risk") == 2).astype(int)
    numeric = tuple(f"a{i}" for i in (2, 5, 8, 11, 16, 18))
    protected = ("a9", "a13", "a20")
    categorical = tuple(f"a{i}" for i in range(1, 21) if f"a{i}" not in {*numeric, *protected})
    return DatasetBundle(
        key="uci_statlog_german",
        frame=frame,
        target="default_12m",
        numeric_features=numeric,
        categorical_features=categorical,
        protected_attributes=protected,
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
        licence="CC BY 4.0",
        attribution=(
            "Hofmann, H. (1994), Statlog German Credit Data, UCI ML Repository, "
            "DOI 10.24432/C5NC77."
        ),
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "Legacy record used only for source-validation exercises. UCI's South German Credit "
            "documentation reports severe coding-information errors in this version; no dates are "
            "available, protected historical fields require review, and it is not the preferred benchmark."
        ),
        quality_spec=QualitySpec(
            ranges={"a2": (1.0, 120.0), "a5": (0.0, None)},
            allowed_values={
                column: frozenset(frame[column].dropna().unique()) for column in categorical
            },
            forbidden_model_columns=frozenset(protected),
        ),
    )


def _taiwan_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        TAIWAN_URL,
        TAIWAN_ZIP_SHA256,
        cache_dir / "uci_taiwan_credit_card" / "taiwan_credit_card.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("default of credit card clients.xls")
    try:
        frame = pd.read_excel(io.BytesIO(raw), header=1, engine="xlrd")
    except ImportError as exc:
        raise ImportError(
            "Install optional dataset support with: pip install -e '.[datasets]'"
        ) from exc
    frame.columns = [_normalise_name(column) for column in frame.columns]
    target_candidates = [
        column for column in frame.columns if "default" in column and column != "id"
    ]
    if len(target_candidates) != 1:
        raise ValueError(f"Could not identify the Taiwan target column: {target_candidates}")
    target_source = target_candidates[0]
    frame = frame.rename(columns={"id": "application_id", target_source: "default_12m"})
    frame["application_id"] = frame["application_id"].map(lambda value: f"TCC-{int(value):06d}")
    protected = tuple(
        column for column in ("sex", "education", "marriage", "age") if column in frame
    )
    excluded = {"application_id", "default_12m", *protected}
    numeric = tuple(column for column in frame.columns if column not in excluded)
    return DatasetBundle(
        key="uci_taiwan_credit_card",
        frame=frame,
        target="default_12m",
        numeric_features=numeric,
        categorical_features=(),
        protected_attributes=protected,
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients",
        licence="CC BY 4.0",
        attribution="Yeh, I. (2009), Default of Credit Card Clients, UCI ML Repository, DOI 10.24432/C55S3H.",
        source_sha256=_sha256_bytes(raw),
        limitations="2005 Taiwan sample; no origination date; demographic variables are excluded from the baseline model.",
        quality_spec=QualitySpec(
            ranges={"limit_bal": (0.0, None)},
            allowed_values={},
            forbidden_model_columns=frozenset(protected),
        ),
    )


def _kaggle_bundle(data_path: Path) -> DatasetBundle:
    if not data_path.exists():
        raise FileNotFoundError(
            f"Kaggle file not found: {data_path}. Download it with your own Kaggle account "
            "after reviewing the current CC0 dataset page. See data/README.md."
        )
    frame = pd.read_csv(data_path)
    required = {
        "person_age",
        "person_income",
        "person_home_ownership",
        "person_emp_length",
        "loan_intent",
        "loan_grade",
        "loan_amnt",
        "loan_int_rate",
        "loan_status",
        "loan_percent_income",
        "cb_person_default_on_file",
        "cb_person_cred_hist_length",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            f"The Kaggle file does not match the reviewed schema; missing {sorted(missing)}"
        )
    frame = frame.copy()
    frame.insert(0, "application_id", [f"KCR-{i:07d}" for i in range(len(frame))])
    frame = frame.rename(columns={"loan_status": "default_12m"})
    return DatasetBundle(
        key="kaggle_credit_risk",
        frame=frame,
        target="default_12m",
        numeric_features=(
            "person_income",
            "person_emp_length",
            "loan_amnt",
            "loan_int_rate",
            "loan_percent_income",
            "cb_person_cred_hist_length",
        ),
        categorical_features=(
            "person_home_ownership",
            "loan_intent",
            "loan_grade",
            "cb_person_default_on_file",
        ),
        protected_attributes=("person_age",),
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://www.kaggle.com/datasets/laotse/credit-risk-dataset",
        licence="CC0 1.0 as displayed by Kaggle on 2026-08-02",
        attribution="Credit Risk Dataset, Kaggle, dataset owner laotse, accessed 2026-08-02.",
        source_sha256=_sha256_file(data_path),
        limitations="Simulated credit-bureau-style data; no dates; provenance and Kaggle metadata require release review.",
        quality_spec=QualitySpec(
            ranges={
                "person_income": (0.0, None),
                "person_emp_length": (0.0, 65.0),
                "loan_amnt": (0.0, None),
                "loan_percent_income": (0.0, 2.0),
            },
            allowed_values={
                column: frozenset(frame[column].dropna().unique())
                for column in (
                    "person_home_ownership",
                    "loan_intent",
                    "loan_grade",
                    "cb_person_default_on_file",
                )
            },
            forbidden_model_columns=frozenset({"person_age"}),
        ),
    )


def _credit_approval_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        CREDIT_APPROVAL_URL,
        CREDIT_APPROVAL_ZIP_SHA256,
        cache_dir / "uci_credit_approval" / "credit_approval.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("crx.data")
    columns = [f"a{i}" for i in range(1, 17)]
    frame = pd.read_csv(io.BytesIO(raw), names=columns, na_values="?")
    frame.insert(0, "application_id", [f"UCA-{i:04d}" for i in range(len(frame))])
    frame["approved"] = (frame.pop("a16") == "+").astype(int)
    numeric = ("a2", "a3", "a8", "a11", "a14", "a15")
    for feature in numeric:
        frame[feature] = pd.to_numeric(frame[feature], errors="coerce")
    categorical = tuple(f"a{i}" for i in (1, 4, 5, 6, 7, 9, 10, 12, 13))
    return DatasetBundle(
        key="uci_credit_approval",
        frame=frame,
        target="approved",
        numeric_features=numeric,
        categorical_features=categorical,
        protected_attributes=(),
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/27/credit+approval",
        licence="CC BY 4.0",
        attribution="Quinlan, J. (1987), Credit Approval, UCI ML Repository, DOI 10.24432/C5FS30.",
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "The target is approval, not default; fields are deliberately anonymised; no dates, economics, "
            "or protected-attribute definitions are available. Use for missing-data and pipeline exercises only."
        ),
        quality_spec=QualitySpec(forbidden_model_columns=frozenset()),
    )


def _australian_approval_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        AUSTRALIAN_APPROVAL_URL,
        AUSTRALIAN_APPROVAL_ZIP_SHA256,
        cache_dir / "uci_australian_credit_approval" / "australian_credit_approval.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("australian.dat")
    columns = [f"a{i}" for i in range(1, 16)]
    frame = pd.read_csv(io.BytesIO(raw), sep=r"\s+", names=columns)
    frame.insert(0, "application_id", [f"AUS-{i:04d}" for i in range(len(frame))])
    frame["approved"] = frame.pop("a15").astype(int)
    numeric = tuple(f"a{i}" for i in (2, 3, 7, 10, 13, 14))
    categorical = tuple(f"a{i}" for i in (1, 4, 5, 6, 8, 9, 11, 12))
    for feature in categorical:
        frame[feature] = frame[feature].astype("category")
    return DatasetBundle(
        key="uci_australian_credit_approval",
        frame=frame,
        target="approved",
        numeric_features=numeric,
        categorical_features=categorical,
        protected_attributes=(),
        id_column="application_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url=("https://archive.ics.uci.edu/dataset/143/statlog+australian+credit+approval"),
        licence="CC BY 4.0",
        attribution=(
            "Quinlan, J. (1987), Statlog Australian Credit Approval, "
            "UCI ML Repository, DOI 10.24432/C59012."
        ),
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "The target is application approval, not default. Attribute meanings are anonymised, "
            "there are no dates or economics, and the published data file already contains the "
            "source's mean/mode replacements for originally missing values."
        ),
        quality_spec=QualitySpec(
            allowed_values={
                feature: frozenset(frame[feature].dropna().unique()) for feature in categorical
            },
            forbidden_model_columns=frozenset(),
        ),
    )


def _polish_bankruptcy_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        POLISH_BANKRUPTCY_URL,
        POLISH_BANKRUPTCY_ZIP_SHA256,
        cache_dir / "uci_polish_bankruptcy" / "polish_bankruptcy.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("5year.arff")
    parsed, _ = arff.loadarff(io.StringIO(raw.decode("utf-8")))
    frame = pd.DataFrame(parsed)
    frame.columns = [_normalise_name(column) for column in frame.columns]
    frame.insert(0, "company_id", [f"POL-5Y-{i:05d}" for i in range(len(frame))])
    frame["bankrupt_within_1y"] = frame.pop("class").map(
        lambda value: int(value.decode("utf-8") if isinstance(value, bytes) else value)
    )
    numeric = tuple(f"attr{i}" for i in range(1, 65))
    return DatasetBundle(
        key="uci_polish_bankruptcy",
        frame=frame,
        target="bankrupt_within_1y",
        numeric_features=numeric,
        categorical_features=(),
        protected_attributes=(),
        id_column="company_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/365/polish+companies+bankruptcy+data",
        licence="CC BY 4.0",
        attribution="Tomczak, S. (2016), Polish Companies Bankruptcy, UCI ML Repository, DOI 10.24432/C5F600.",
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "This adapter uses the 5th-year file (one-year forecast horizon). It is highly imbalanced, "
            "contains missing ratios, and has no entity dates for an out-of-time split."
        ),
        quality_spec=QualitySpec(forbidden_model_columns=frozenset()),
    )


def _taiwan_bankruptcy_bundle(cache_dir: Path) -> DatasetBundle:
    archive = _download_checked(
        TAIWAN_BANKRUPTCY_URL,
        TAIWAN_BANKRUPTCY_ZIP_SHA256,
        cache_dir / "uci_taiwan_bankruptcy" / "taiwan_bankruptcy.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        raw = zipped.read("data.csv")
    frame = pd.read_csv(io.BytesIO(raw))
    frame.columns = [_normalise_name(column) for column in frame.columns]
    target_source = next(column for column in frame.columns if column.startswith("bankrupt"))
    frame.insert(0, "company_id", [f"TWB-{i:05d}" for i in range(len(frame))])
    frame["bankrupt"] = frame.pop(target_source).astype(int)
    numeric = tuple(column for column in frame.columns if column not in {"company_id", "bankrupt"})
    return DatasetBundle(
        key="uci_taiwan_bankruptcy",
        frame=frame,
        target="bankrupt",
        numeric_features=numeric,
        categorical_features=(),
        protected_attributes=(),
        id_column="company_id",
        date_column=None,
        split_strategy="stratified_random_no_time_available",
        source_url="https://archive.ics.uci.edu/dataset/572/taiwanese+bankruptcy+prediction",
        licence="CC BY 4.0",
        attribution="Taiwanese Bankruptcy Prediction (2020), UCI ML Repository, dataset 572.",
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "Company bankruptcy is not borrower default. The sample covers 1999-2009 and does not include "
            "observation dates or a lender decision process. Use for low-event corporate modelling exercises."
        ),
        quality_spec=QualitySpec(forbidden_model_columns=frozenset()),
    )


def _bank_marketing_bundle(cache_dir: Path) -> DatasetBundle:
    """Load the dated-order Bank Marketing file for non-credit exercises.

    The response is term-deposit subscription, not loan approval or default. The
    post-call duration field is retained for a leakage exercise but excluded from
    admissible model features.
    """

    archive = _download_checked(
        BANK_MARKETING_URL,
        BANK_MARKETING_ZIP_SHA256,
        cache_dir / "uci_bank_marketing" / "bank_marketing.zip",
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as outer:
        nested = outer.read("bank-additional.zip")
    with zipfile.ZipFile(io.BytesIO(nested)) as inner:
        raw = inner.read("bank-additional/bank-additional-full.csv")
    frame = pd.read_csv(io.BytesIO(raw), sep=";")
    frame.columns = [_normalise_name(column) for column in frame.columns]
    frame.insert(0, "contact_id", [f"BMK-{i:05d}" for i in range(len(frame))])
    frame["subscribed"] = (frame.pop("y") == "yes").astype(int)
    protected = ("age", "marital")
    numeric = (
        "campaign",
        "pdays",
        "previous",
        "emp_var_rate",
        "cons_price_idx",
        "cons_conf_idx",
        "euribor3m",
        "nr_employed",
    )
    categorical = (
        "job",
        "education",
        "default",
        "housing",
        "loan",
        "contact",
        "month",
        "day_of_week",
        "poutcome",
    )
    return DatasetBundle(
        key="uci_bank_marketing",
        frame=frame,
        target="subscribed",
        numeric_features=numeric,
        categorical_features=categorical,
        protected_attributes=protected,
        id_column="contact_id",
        date_column=None,
        split_strategy="ordered_source_sequence_no_exact_dates",
        source_url="https://archive.ics.uci.edu/dataset/222/bank+marketing",
        licence="CC BY 4.0",
        attribution=(
            "Moro, S., Rita, P., & Cortez, P. (2014), Bank Marketing, "
            "UCI ML Repository, DOI 10.24432/C5K306."
        ),
        source_sha256=_sha256_bytes(raw),
        limitations=(
            "The target is term-deposit subscription, not credit approval, bankruptcy or default. "
            "Rows are ordered by source chronology but exact dates are unavailable. Contact duration "
            "is known only after the call and is excluded from any pre-call model."
        ),
        quality_spec=QualitySpec(
            ranges={"campaign": (1.0, None), "previous": (0.0, None)},
            allowed_values={
                column: frozenset(frame[column].dropna().unique()) for column in categorical
            },
            forbidden_model_columns=frozenset({"age", "marital", "duration"}),
        ),
    )


def available_datasets() -> tuple[str, ...]:
    return (
        "synthetic_retail",
        "uci_south_german",
        "uci_statlog_german",
        "uci_taiwan_credit_card",
        "uci_credit_approval",
        "uci_australian_credit_approval",
        "uci_polish_bankruptcy",
        "uci_taiwan_bankruptcy",
        "uci_bank_marketing",
        "kaggle_credit_risk",
    )


def load_dataset(
    key: str,
    *,
    data_path: str | Path | None = None,
    cache_dir: str | Path = "data/raw",
    n_rows: int = 5_000,
    seed: int = 42,
) -> DatasetBundle:
    """Load one reviewed dataset through a stable modelling contract."""

    if key == "synthetic_retail":
        return _synthetic_bundle(n_rows=n_rows, seed=seed)
    if key == "uci_south_german":
        return _south_german_bundle(Path(cache_dir))
    if key == "uci_statlog_german":
        return _statlog_german_bundle(Path(cache_dir))
    if key == "uci_taiwan_credit_card":
        return _taiwan_bundle(Path(cache_dir))
    if key == "uci_credit_approval":
        return _credit_approval_bundle(Path(cache_dir))
    if key == "uci_australian_credit_approval":
        return _australian_approval_bundle(Path(cache_dir))
    if key == "uci_polish_bankruptcy":
        return _polish_bankruptcy_bundle(Path(cache_dir))
    if key == "uci_taiwan_bankruptcy":
        return _taiwan_bankruptcy_bundle(Path(cache_dir))
    if key == "uci_bank_marketing":
        return _bank_marketing_bundle(Path(cache_dir))
    if key == "kaggle_credit_risk":
        path = Path(data_path) if data_path else Path(cache_dir) / key / "credit_risk_dataset.csv"
        return _kaggle_bundle(path)
    raise KeyError(
        f"Unknown dataset {key!r}. Available datasets: {', '.join(available_datasets())}"
    )
