"""Tests for reproducible analysis records."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

import stmpy


SAMPLE_DATA = (
    Path(__file__).resolve().parents[1] / "stmpy" / "doc" / "tutorial_materials"
)


class AnalysisRecordTests(unittest.TestCase):
    def test_real_sxm_load_records_file_and_array_shapes(self):
        source = SAMPLE_DATA / "topo.sxm"
        record = stmpy.AnalysisRecord(
            "topography check",
            parameters={"temperature_K": np.float64(4.2)},
        )

        data = stmpy.load(source, record=record)

        expected_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertEqual(record.inputs[0]["name"], "topo.sxm")
        self.assertEqual(record.inputs[0]["sha256"], expected_hash)
        self.assertEqual(record.steps[0]["name"], "load")
        self.assertEqual(
            record.steps[0]["result"]["arrays"]["Z"]["shape"],
            list(data.Z.shape),
        )

    def test_save_tracks_output_and_writes_valid_json(self):
        record = stmpy.AnalysisRecord(
            "linecut export",
            parameters={"energy_window_meV": [-5, 5]},
        )

        with tempfile.TemporaryDirectory() as directory:
            output_path = Path(directory) / "processed.spy"
            record_path = Path(directory) / "processed.analysis.json"
            stmpy.save({"energy": np.array([-1.0, 0.0, 1.0])}, output_path,
                       record=record)
            saved_path = record.save(record_path)
            payload = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["analysis_name"], "linecut export")
        self.assertEqual(payload["stmpy_version"], stmpy.__version__)
        self.assertEqual(payload["outputs"][0]["name"], "processed.spy")
        self.assertEqual(len(payload["outputs"][0]["sha256"]), 64)
        self.assertEqual(payload["steps"][0]["name"], "save")

    def test_missing_provenance_file_has_clear_error(self):
        record = stmpy.AnalysisRecord("missing input check")

        with self.assertRaisesRegex(FileNotFoundError, "does not exist"):
            record.add_input("missing.sxm")

    def test_name_cannot_be_blank(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            stmpy.AnalysisRecord("  ")


if __name__ == "__main__":
    unittest.main()
