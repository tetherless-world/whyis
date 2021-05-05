#!/usr/bin/env python

from distutils.core import setup

setup(name='{{cookiecutter.project_name}}',
      version='{{cookiecutter.version}}',
      description='{{cookiecutter.project_short_description}}',
      author='{{cookiecutter.author}}',
      packages=[
          {% for package in cookiecutter.packages.split(',') if package.strip()|length > 0 %}"{{package.strip()}}",
          {% endfor %}
          ],
     )
