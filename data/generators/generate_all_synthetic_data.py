from pathlib import Path

from fraud_generator import create_synthetic_fraud_dataset
from lgd_generator import create_synthetic_lgd_dataset
from ead_generator import create_synthetic_ead_dataset
from bnpl_microloan_generator import create_synthetic_bnpl_microloan_dataset
from ifrs9_cohort_generator import create_synthetic_ifrs9_cohort_dataset


OUTPUT_DIR = Path("data/synthetic")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    datasets = {
        "synthetic_fraud_transactions.csv": create_synthetic_fraud_dataset(),
        "synthetic_lgd.csv": create_synthetic_lgd_dataset(),
        "synthetic_ead.csv": create_synthetic_ead_dataset(),
        "synthetic_bnpl_microloan.csv": create_synthetic_bnpl_microloan_dataset(),
        "synthetic_ifrs9_cohort.csv": create_synthetic_ifrs9_cohort_dataset(),
    }

    for filename, df in datasets.items():
        output_path = OUTPUT_DIR / filename
        df.to_csv(output_path, index=False)
        print(f"Saved {filename}: {df.shape}")


if __name__ == "__main__":
    main()
