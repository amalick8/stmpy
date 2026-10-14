"""Tests for public file-type dispatch in :mod:`stmpy.io`."""

import unittest
from unittest import mock

from stmpy import io


class FileDispatchTests(unittest.TestCase):
    def setUp(self):
        self.loaders = io._LOADERS.copy()
        self.savers = io._SAVERS.copy()

    def tearDown(self):
        io._LOADERS.clear()
        io._LOADERS.update(self.loaders)
        io._SAVERS.clear()
        io._SAVERS.update(self.savers)

    def test_load_uses_registered_loader(self):
        sentinel = object()
        calls = []

        def load_dat(path):
            calls.append(path)
            return sentinel

        io._LOADERS['dat'] = load_dat

        with mock.patch.object(io.os.path, 'isfile', return_value=True):
            result = io.load('measurement.run.dat', biasOffset=False)

        self.assertIs(result, sentinel)
        self.assertEqual(calls, ['measurement.run.dat'])

    def test_load_rejects_missing_extension(self):
        with self.assertRaisesRegex(OSError, 'filename extension'):
            io.load('measurement')

    def test_load_rejects_unsupported_extension(self):
        with self.assertRaisesRegex(OSError, "cannot load '.csv'"):
            io.load('measurement.csv')

    def test_load_reports_missing_file(self):
        with self.assertRaisesRegex(FileNotFoundError, 'missing.dat'):
            io.load('missing.dat', biasOffset=False)

    def test_save_uses_registered_saver(self):
        calls = []

        def save_spy(data, path, objects):
            calls.append((data, path, objects))

        io._SAVERS['spy'] = save_spy
        payload = {'channel': 'Z'}
        objects = [io.Spy]

        io.save(payload, 'result.spy', objects)

        self.assertEqual(calls, [(payload, 'result.spy', objects)])

    def test_save_rejects_missing_extension(self):
        with self.assertRaisesRegex(OSError, 'filename extension'):
            io.save({}, 'result')

    def test_save_rejects_unsupported_extension(self):
        with self.assertRaisesRegex(OSError, "cannot save '.csv'"):
            io.save({}, 'result.csv')


if __name__ == '__main__':
    unittest.main()
