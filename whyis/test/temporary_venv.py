import os.path
import shutil
import subprocess
import tempfile
import venv

class TemporaryVenv:
    def __init__(self, delete=True, install_whyis_requirements=True, whyis_dir_path=None):
        self.__delete = delete
        self.__install_whyis_requirements = install_whyis_requirements

        self.venv_dir_path = None

        if whyis_dir_path is None:
            from whyis import manager
            whyis_dir_path = os.path.dirname(manager.__file__)
        self.whyis_dir_path = whyis_dir_path

    def __enter__(self):
        temp_venv_dir_path = os.path.join(self.whyis_dir_path, "tmpvenv")
        if not os.path.isdir(temp_venv_dir_path):
            os.makedirs(temp_venv_dir_path)
        self.venv_dir_path = tempfile.mkdtemp(dir=temp_venv_dir_path)
        # print(self.venv_dir_path)
        venv.create(self.venv_dir_path)
        # with_pip doesn't work at present, so have to install pip into it manually
        subprocess.call("bash -c 'source %s/bin/activate && curl https://bootstrap.pypa.io/get-pip.py | python'" % self.venv_dir_path, cwd=self.whyis_dir_path, shell=True)
        if self.__install_whyis_requirements:
            self.install_whyis_requirements()
        return self

    def __exit__(self, *args, **kwds):
        if self.__delete:
            shutil.rmtree(self.venv_dir_path)

    def install_whyis_requirements(self) -> None:
        # Install every requirement separately so that failed installations are skipped
        # subprocess.call("cat requirements/common.txt | xargs -n 1 %s/bin/pip install" % self.venv_dir_path, cwd=self.whyis_dir_path, shell=True)
        subprocess.call("%s/bin/pip install --progress-bar off -e .." % (self.venv_dir_path), cwd=self.whyis_dir_path, shell=True)

    def is_whyis_app_installed(self) -> bool:
        return subprocess.call("%s/bin/python -c 'import config'" % self.venv_dir_path, cwd=self.whyis_dir_path, shell=True) == 0
