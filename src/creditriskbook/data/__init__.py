"""Dataset adapters, synthetic generation, and data-quality controls."""

from .behavioral import BehavioralDataset, inject_behavioral_defects, make_behavioral_credit_history
from .datasets import DatasetBundle, available_datasets, load_dataset
from .documents import SyntheticCreditDocumentCase, make_synthetic_credit_document_case
from .portfolios import CaseDataset, available_case_datasets, load_case_dataset
from .public_data import PublicDataBundle, load_cfpb_complaint_extract, load_world_bank_wdi
from .quality import DefectInjectionResult, inject_teaching_defects_with_manifest

__all__ = [
    "BehavioralDataset",
    "CaseDataset",
    "DatasetBundle",
    "DefectInjectionResult",
    "PublicDataBundle",
    "SyntheticCreditDocumentCase",
    "available_case_datasets",
    "available_datasets",
    "load_case_dataset",
    "load_dataset",
    "load_cfpb_complaint_extract",
    "load_world_bank_wdi",
    "inject_behavioral_defects",
    "inject_teaching_defects_with_manifest",
    "make_behavioral_credit_history",
    "make_synthetic_credit_document_case",
]
