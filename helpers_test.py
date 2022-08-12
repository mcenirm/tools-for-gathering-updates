"""Unit tests for helpers.py"""
import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import kits.helpers as helpers


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


class GitTests(unittest.TestCase):
    """Test git-related helpers"""

    ANONYMITY_NAME = "Example Nobody"
    ANONYMITY_EMAIL = "nobody@example.com"
    ANONYMITY_ENV = dict(
        GIT_AUTHOR_NAME=ANONYMITY_NAME,
        GIT_AUTHOR_EMAIL=ANONYMITY_EMAIL,
        GIT_COMMITTER_NAME=ANONYMITY_NAME,
        GIT_COMMITTER_EMAIL=ANONYMITY_EMAIL,
    )

    @staticmethod
    def _run_git(git_args: list[str], **kwargs) -> subprocess.CompletedProcess:
        # avoid modifying original kwargs
        kwargs = dict(kwargs)
        env = GitTests.ANONYMITY_ENV | kwargs.pop("env", {})
        check = kwargs.pop("check", True)
        return subprocess.run(["git"] + git_args, check=check, env=env, **kwargs)

    @staticmethod
    def _init_and_commit(work_dir: Path, initial_branch: str):
        work_dir.mkdir(parents=True, exist_ok=True)
        for args in [
            ["init"],
            ["checkout", "-b", initial_branch],
            ["commit", "--allow-empty", "-n", "-m", "initial"],
        ]:
            GitTests._run_git(args, cwd=work_dir)

    def test_git_url_basename(self):
        """Test git_url_basename

        Some test data is from header doc for git_url_basename in git source code
        """
        for git_url, expected_basename in [
            ("/path/to/repo.git", "repo"),
            ("host.xz:foo/.git", "foo"),
            ("http://example.com/user/bar.baz", "bar.baz"),
            ("git@example.com:user/foo.git", "foo"),
            ("https://example.com/user/foo.git", "foo"),
        ]:
            with self.subTest():
                self.assertEqual(
                    expected_basename, helpers.git_url_basename(git_url), git_url
                )

    def test_git_branch_show_current(self):
        """Test git_branch_show_current"""
        with tempfile.TemporaryDirectory() as tmpdir:
            branch_name = "something-other-than-the-default"
            GitTests._init_and_commit(Path(tmpdir), branch_name)
            self.assertEqual(branch_name, helpers.git_branch_show_current(tmpdir))

    def test_git_clone(self):
        """Test git_clone"""
        with tempfile.TemporaryDirectory() as tmpdir:
            origin = Path(tmpdir, "origin")
            cloned = Path(tmpdir, "cloned")
            branch_name = "main"
            GitTests._init_and_commit(origin, branch_name)
            details = helpers.git_clone(str(origin), work_dir=cloned)
            self.assertEqual(cloned, details.path)
            self.assertEqual(origin, Path(details.remote_url))
            self.assertEqual(branch_name, details.initial_branch)


if __name__ == "__main__":
    unittest.main()
