"""
Essential data loaders for the book:
Credit Risk Modeling for Basel and IFRS 9 using Python.
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_openml_german_credit():
    """
    Load German Credit dataset from OpenML.

    Returns
    -------
    pandas.DataFrame
        Dataset with an added binary target column: default.
    """
    from sklearn.datasets import fetch_openml

    data = fetch_openml(name="credit-g", version=1, as_frame=True)
    df = data.frame.copy()

    df["default"] = (df["class"] == "bad").astype(int)

    return df


def load_uci_german_credit():
    """
    Load German Credit dataset from UCI.

    Returns
    -------
    pandas.DataFrame
        UCI German Credit dataset.
    """
    from ucimlrepo import fetch_ucirepo

    dataset = fetch_ucirepo(id=144)

    X = dataset.data.features
    y = dataset.data.targets

    df = pd.concat([X, y], axis=1)

    return df


def load_synthetic_fraud(path=None):
    """
    Load synthetic fraud dataset from local CSV.

    Parameters
    ----------
    path : str or None
        Optional custom path.

    Returns
    -------
    pandas.DataFrame
    """
    if path is None:
        path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_fraud_transactions.csv"

    return pd.read_csv(path)


def load_world_bank_macro(
    countries=None,
    start_year=2000,
    end_year=2023
):
    """
    Load macroeconomic data from World Bank.

    Parameters
    ----------
    countries : list or None
        Country ISO3 codes.
    start_year : int
        Start year.
    end_year : int
        End year.

    Returns
    -------
    pandas.DataFrame
    """
    import wbgapi as wb

    if countries is None:
        countries = ["USA", "GBR", "DEU", "FRA", "GRC"]

    indicators = {
        "NY.GDP.MKTP.KD.ZG": "gdp_growth",
        "FP.CPI.TOTL.ZG": "inflation",
        "SL.UEM.TOTL.ZS": "unemployment"
    }

    raw = wb.data.DataFrame(
        list(indicators.keys()),
        economy=countries,
        time=range(start_year, end_year + 1),
        labels=True
    )

    return raw


def save_dataframe(df, path):
    """
    Save DataFrame to CSV and create folders if needed.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def load_csv(path):
    """
    Load a local CSV file.
    """
    return pd.read_csv(path)

def load_synthetic_lgd(path=None):
    """
    Load synthetic LGD dataset.
    """
    if path is None:
        path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_lgd.csv"

    return pd.read_csv(path)


def load_synthetic_ead(path=None):
    """
    Load synthetic EAD dataset.
    """
    if path is None:
        path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_ead.csv"

    return pd.read_csv(path)


def load_synthetic_bnpl_microloan(path=None):
    """
    Load synthetic BNPL and microloan dataset.
    """
    if path is None:
        path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_bnpl_microloan.csv"

    return pd.read_csv(path)


def load_synthetic_ifrs9_cohort(path=None):
    """
    Load synthetic IFRS 9 cohort dataset.
    """
    if path is None:
        path = PROJECT_ROOT / "data" / "synthetic" / "synthetic_ifrs9_cohort.csv"

    return pd.read_csv(path)
