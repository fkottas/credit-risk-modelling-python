from __future__ import annotations

import os
import tempfile
import unittest

from creditriskbook.data.datasets import load_dataset


@unittest.skipUnless(
    os.getenv("RUN_LIVE_DATA_TESTS") == "1",
    "Set RUN_LIVE_DATA_TESTS=1 to access and verify authoritative publisher files.",
)
class LiveDatasetTests(unittest.TestCase):
    def test_south_german_download_checksum_schema_and_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = load_dataset("uci_south_german", cache_dir=directory)
        self.assertEqual(bundle.frame.shape, (1_000, 22))
        self.assertEqual(
            bundle.frame[bundle.target].value_counts().sort_index().to_dict(), {0: 700, 1: 300}
        )
        self.assertEqual(
            bundle.source_sha256,
            "5f363343f356ca38a0236baab849e472846399b2176ccc5bd686483dd8a7562f",
        )

    def test_taiwan_download_checksum_schema_and_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = load_dataset("uci_taiwan_credit_card", cache_dir=directory)
        self.assertEqual(bundle.frame.shape, (30_000, 25))
        self.assertEqual(
            bundle.frame[bundle.target].value_counts().sort_index().to_dict(),
            {0: 23_364, 1: 6_636},
        )
        self.assertEqual(
            bundle.source_sha256,
            "30c6be3abd8dcfd3e6096c828bad8c2f011238620f5369220bd60cfc82700933",
        )

    def test_credit_approval_download_schema_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = load_dataset("uci_credit_approval", cache_dir=directory)
        self.assertEqual(bundle.frame.shape, (690, 17))
        self.assertEqual(
            bundle.frame[bundle.target].value_counts().sort_index().to_dict(), {0: 383, 1: 307}
        )
        self.assertEqual(
            bundle.source_sha256, "fff49bc186cbddb3ace7371d40d9fbbb3af4f126019c13ff3f562249b1454f4d"
        )

    def test_polish_bankruptcy_download_schema_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = load_dataset("uci_polish_bankruptcy", cache_dir=directory)
        self.assertEqual(bundle.frame.shape, (5_910, 66))
        self.assertEqual(
            bundle.frame[bundle.target].value_counts().sort_index().to_dict(), {0: 5_500, 1: 410}
        )
        self.assertEqual(
            bundle.source_sha256, "cb3f6f250ac46bd8d18e9a222f489fe8ee3e396fcec18959f5a0ef8e8169b2fc"
        )

    def test_taiwan_bankruptcy_download_schema_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = load_dataset("uci_taiwan_bankruptcy", cache_dir=directory)
        self.assertEqual(bundle.frame.shape, (6_819, 97))
        self.assertEqual(
            bundle.frame[bundle.target].value_counts().sort_index().to_dict(), {0: 6_599, 1: 220}
        )
        self.assertEqual(
            bundle.source_sha256, "67bf2e7c75490f7ad3f76bbce57d49cdc25967cdab607527b94f944863fa14d8"
        )


if __name__ == "__main__":
    unittest.main()
