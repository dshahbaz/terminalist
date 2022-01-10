"""Tests for terminalist.py"""

import io
import pathlib
import re
import tempfile
import shutil
import subprocess
import unittest

import terminalist


# https://no-color.org/
NO_COLOR = "NO_COLOR"


class TestColor(unittest.TestCase):
    def test_colors_stripped(self):
        # Ensure colors are stripped with any value of NO_COLOR given.
        sio = io.StringIO()
        terminalist._color_print(
            "testing", file=sio, color=terminalist.Colors.OKCYAN, _environ={NO_COLOR: "1"}
        )
        self.assertFalse(terminalist.Colors.OKCYAN in sio.getvalue())

        sio = io.StringIO()
        terminalist._color_print(
            "testing", file=sio, color=terminalist.Colors.OKCYAN, _environ={NO_COLOR: "0"}
        )
        self.assertFalse(terminalist.Colors.OKCYAN in sio.getvalue())

        sio = io.StringIO()
        terminalist._color_print(
            "testing", file=sio, color=terminalist.Colors.OKCYAN, _environ={NO_COLOR: 0}
        )
        self.assertFalse(terminalist.Colors.OKCYAN in sio.getvalue())

        sio = io.StringIO()
        terminalist.print_blue("testing", file=sio, _environ={NO_COLOR: "1"})
        self.assertFalse(terminalist.Colors.OKBLUE in sio.getvalue())

    def test_colors_present(self):
        sio = io.StringIO()
        terminalist._color_print("testing", file=sio, color=terminalist.Colors.OKCYAN, _environ={})
        self.assertTrue(terminalist.Colors.OKCYAN in sio.getvalue())

        sio = io.StringIO()
        terminalist.print_blue("testing", file=sio)
        self.assertTrue(terminalist.Colors.OKBLUE in sio.getvalue())

        sio = io.StringIO()
        terminalist.print_cyan("testing", file=sio)
        self.assertTrue(terminalist.Colors.OKCYAN in sio.getvalue())


class TestRunning(unittest.TestCase):
    def test_install_interception(self):
        with tempfile.TemporaryDirectory() as t:
            d = pathlib.Path(t)
            shutil.copy(terminalist.__file__, d)

            terminalist_script = d / "terminalist.py"
            self.assertTrue(terminalist_script.is_file())

            find = d / "find"
            self.assertFalse(find.exists())

            # Test installation:
            subprocess.run([str(terminalist_script), "--install", "find"])

            self.assertTrue(find.exists())
            self.assertTrue(find.is_symlink())
            self.assertEqual(find.resolve(), terminalist_script.resolve())

            # Test removal:
            subprocess.run([str(terminalist_script), "--remove", "find"])
            self.assertFalse(find.exists())

    def test_run_interception(self):
        with tempfile.TemporaryDirectory() as t:
            d = pathlib.Path(t)
            shutil.copy(terminalist.__file__, d)

            terminalist_script = d / "terminalist.py"
            find = d / "find"
            subprocess.run([str(terminalist_script), "--install", "find"])

            find_run = subprocess.run(
                [str(find), "-name", "foo"], stdout=subprocess.PIPE, encoding="utf-8"
            )
            # The command itself should fail, because it does *not* ultimately run `/usr/bin/find`.
            self.assertEqual(1, find_run.returncode)
            # Check that the helpful message about `find -name` is printed out.
            self.assertRegex(find_run.stdout, re.compile("Instead of:.*find.*use:.*fd", re.S))
            self.assertIn("-name", find_run.stdout)
            self.assertIn("<name>", find_run.stdout)
            self.assertIn("The name argument does not have a flag", find_run.stdout)

    def test_install_not_writable(self):
        with tempfile.TemporaryDirectory() as t:
            d = pathlib.Path(t)
            shutil.copy(terminalist.__file__, d)

            terminalist_script = d / "terminalist.py"
            find = d / "find"

            # Remove write bits.
            try:
                d.chmod(0o555)
                install_run = subprocess.run(
                    [str(terminalist_script), "--install", "find"],
                    stdout=subprocess.PIPE,
                    encoding="utf-8",
                )
                self.assertEqual(1, install_run.returncode)
                self.assertIn("not writable", install_run.stdout)
            finally:
                # Restore settings, so that test clean up can happen.
                d.chmod(0o777)


if __name__ == "__main__":
    unittest.main()
