"""Unit tests for helpers.py"""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers


class RmVTests(unittest.TestCase):
    """Unit tests for helpers.rm_v"""

    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        super().setUp()
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base_directory = Path(self.temporary_directory.name)
        self.relative_paths = [Path(_) for _ in ("one.txt", "two/two.txt")]
        self.absolute_paths = [self.base_directory / _ for _ in self.relative_paths]
        for p in self.absolute_paths:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()
        self.captured_stdout = io.StringIO()
        self.captured_stderr = io.StringIO()
        self.mock_unlink = mock.MagicMock()
        self.removed: list[Path] = []

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()
        super().tearDown()

    def call_rm_v(self, *args, **kwargs):
        """convenience wrapper around rm_v to prepare context managers"""
        with mock.patch(
            "pathlib.Path.unlink", self.mock_unlink
        ), contextlib.redirect_stderr(self.captured_stderr), contextlib.redirect_stdout(
            self.captured_stdout
        ):
            self.removed = helpers.rm_v(*args, **kwargs)

    def test_no_args(self) -> None:
        """rm_v() should remove no files, produce no output, and return no results"""
        self.call_rm_v()
        self.assertSequenceEqual(self.removed, [])
        self.assertEqual(self.captured_stderr.getvalue(), "")
        self.assertEqual(self.captured_stdout.getvalue(), "")
        self.assertEqual(self.mock_unlink.call_count, 0)

    def test_basic(self) -> None:
        """basic testing for rm_v"""
        self.call_rm_v(*self.relative_paths, base_directory=self.base_directory)
        self.assertSequenceEqual(self.removed, self.relative_paths)
        self.assertEqual(self.captured_stderr.getvalue(), "")
        self.assertEqual(
            self.captured_stdout.getvalue(),
            "".join((f"removed {repr(str(_))}\n" for _ in self.relative_paths)),
        )
        self.assertEqual(self.mock_unlink.call_count, len(self.relative_paths))


if __name__ == "__main__":
    unittest.main()
