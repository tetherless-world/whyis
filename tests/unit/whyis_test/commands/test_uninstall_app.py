import os.path
import subprocess
import sys
import tempfile
import venv

from whyis.test.temporary_app import TemporaryApp
from whyis.test.temporary_venv import TemporaryVenv
from whyis.test.unit_test_case import UnitTestCase




class TestUninstallApp(UnitTestCase):
    def test_run(self):
        if sys.platform.startswith("linux") or sys.platform.startswith("win"):
            return

        with TemporaryVenv() as temp_venv:
            with TemporaryApp() as temp_app:
                temp_app.install(venv_dir_path=temp_venv.venv_dir_path)
                self.assertTrue(temp_venv.is_whyis_app_installed())

                # Uninstall
                self.assertEqual(0, subprocess.call("bash -c 'source %s/bin/activate && whyis uninstallapp -y'" % (temp_venv.venv_dir_path,), cwd=temp_venv.whyis_dir_path, shell=True))

                self.assertFalse(temp_venv.is_whyis_app_installed())
