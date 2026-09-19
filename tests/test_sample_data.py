"""Regression tests for the sample microscope data shipped with STMPY."""

from pathlib import Path
import tempfile
import unittest

import numpy as np

import stmpy


SAMPLE_DATA = (
    Path(__file__).resolve().parents[1] / 'stmpy' / 'doc' / 'tutorial_materials'
)


class SampleDataTests(unittest.TestCase):
    def test_spy_save_and_load_round_trip(self):
        original = {
            'energy': np.array([-1.0, 0.0, 1.0]),
            'label': 'test',
            'notes': 'first line\nsecond line\n',
        }

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'roundtrip.spy'
            stmpy.save(original, str(path))
            restored = stmpy.load(str(path))

        np.testing.assert_array_equal(restored['energy'], original['energy'])
        self.assertEqual(restored['label'], original['label'])
        self.assertEqual(restored['notes'], original['notes'])

    def test_load_sxm_topography(self):
        data = stmpy.load(str(SAMPLE_DATA / 'topo.sxm'))

        self.assertEqual(data.Z.shape, (256, 256))
        self.assertEqual(data.I.shape, (256, 256))
        self.assertEqual(data.LIY.shape, (256, 256))
        self.assertEqual(data.header['scan_pixels'], [256.0, 256.0])
        np.testing.assert_allclose(data.header['scan_range'], [3e-8, 3e-8])
        self.assertTrue(np.isfinite(data.Z).all())

    def test_load_3ds_spectroscopy_map(self):
        data = stmpy.load(
            str(SAMPLE_DATA / 'testing map.3ds'),
            biasOffset=False,
        )

        self.assertEqual(data.Z.shape, (256, 256))
        self.assertEqual(data.I.shape, (10, 256, 256))
        self.assertEqual(data.LIY.shape, (10, 256, 256))
        self.assertEqual(data.en.shape, (10,))
        np.testing.assert_allclose(
            data.en[[0, -1]],
            [-0.60000002, -0.1],
            rtol=0,
            atol=1e-7,
        )
        self.assertTrue(np.isfinite(data.I).all())
        self.assertTrue(np.isfinite(data.LIY).all())


if __name__ == '__main__':
    unittest.main()
