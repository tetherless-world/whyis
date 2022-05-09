import os.path
import shutil
import subprocess
import tempfile


class TemporaryApp:
    def __init__(self, delete=True):
        self.__delete = delete
        self.app_dir_path = None

    def __enter__(self):
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
from whyis.config_defaults import *
""")

        # print(self.app_dir_path)

        return self

    def __exit__(self, *args, **kwds):
        if self.__delete:
            shutil.rmtree(self.app_dir_path)

    def install(self, venv_dir_path: str):
        subprocess.call("%s/bin/pip install -e ." % venv_dir_path, cwd=self.app_dir_path, shell=True)
