from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

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
        self.assertEqual(bundle.frame[bundle.target].value_counts().sort_index().to_dict(), {0: 700, 1: 300})
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


if __name__ == "__main__":
    unittest.main()

