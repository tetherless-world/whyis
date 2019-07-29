import os.path
import subprocess
import sys
import tempfile
import venv

from whyis.test.unit_test_case import UnitTestCase



class TemporaryApp:
    def __init__(self):
        self.app_dir_path = None
        self.venv_dir_path = None
        import manage
        self.whyis_dir_path = os.path.dirname(manage.__file__)

    def __enter__(self):
        # Create a temporary venv so we don't interfere with the actual venv
        temp_venv_dir_path = os.path.join(self.whyis_dir_path, "tmpvenv")
        if not os.path.isdir(temp_venv_dir_path):
            os.makedirs(temp_venv_dir_path)
        self.venv_dir_path = tempfile.mkdtemp(dir=temp_venv_dir_path)
        venv.create(self.venv_dir_path)
        subprocess.call("source %s/bin/activate && pip install -r requirements/common.txt" % self.venv_dir_path, cwd=self.whyis_dir_path, shell=True)

        # Create a temporary application
        self.app_dir_path = tempfile.mkdtemp()
        with open(os.path.join(self.app_dir_path, "setup.py"), "w+") as setup_py_file:
            setup_py_file.write("""\
from distutils.core import setup            
            
setup(name='TempApp',
      version='0.1',
      description='Temporary app',
      author='rui',
      packages=[

      ],
      )
""")

        with open(os.path.join(self.app_dir_path, "config.py"), "w+") as config_py_file:
            config_py_file.write("""\
answer = 42
""")

        return self

    def __exit__(self, *args, **kwds):
        pass
    #     self.tempdir.__exit__(*args, **kwds)

    def install(self):
        subprocess.call("source %s/bin/activate && pip install -e ." % self.venv_dir_path, cwd=self.app_dir_path, shell=True)


class TestUninstallApp(UnitTestCase):
    def test_run(self):
        if sys.platform.startswith("win"):
            return

        with TemporaryApp() as temp_app:
            temp_app.install()

            # Check app installed
            print(temp_app.venv_dir_path)
            self.assertEqual(42, subprocess.call("%s/bin/python -c 'import config; import sys; sys.exit(config.answer)'" % temp_app.venv_dir_path, cwd=temp_app.whyis_dir_path, shell=True))
            # Uninstall
            self.assertEqual(0, subprocess.call("%s/bin/python manage.py -y uninstall_app" % temp_app.venv_dir_path, cwd=temp_app.whyis_dir_path, shell=True))
            # Check app uninstalled
            self.assertNotEqual(0, subprocess.call("%s/bin/python -c 'import config'" % temp_app.venv_dir_path, cwd=temp_app.whyis_dir_path, shell=True))
