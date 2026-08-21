"""Dataset adapters, synthetic generation, and data-quality controls."""

from .behavioral import BehavioralDataset, inject_behavioral_defects, make_behavioral_credit_history
from .datasets import DatasetBundle, available_datasets, load_dataset
from .documents import SyntheticCreditDocumentCase, make_synthetic_credit_document_case
from .portfolios import CaseDataset, available_case_datasets, load_case_dataset

__all__ = [
    "BehavioralDataset",
    "CaseDataset",
    "DatasetBundle",
    "SyntheticCreditDocumentCase",
    "available_case_datasets",
    "available_datasets",
    "load_case_dataset",
    "load_dataset",
    "inject_behavioral_defects",
    "make_behavioral_credit_history",
    "make_synthetic_credit_document_case",
]
