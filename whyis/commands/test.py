# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask

import os


class Test(Command):
    """
    Run tests
    """

    ci = False
    verbosity = 2
    failfast = False
    tests = 'test*'
    apponly = False

    def get_options(self):
        return [
            Option('-v', '--verbosity', dest='verbosity', help='verbosity level of output, between 0 and 2 (default 2)',
                   type=int, default=self.verbosity),
            Option('--failfast', dest='failfast', help='Stop the test after the first failure',
                   default=self.failfast, action='store_false'),
            Option('--test', dest='tests', help='Name of python file (without extension) to run tests from, or glob pattern',
                   default=self.tests, type=str),
            Option('--ci', dest='ci', default=self.ci, help='Analyze coverage and store all results as XML (for CI server)', action='store_true'),
            Option('--apponly', dest='apponly', default=self.apponly, help='Runs the app tests only', action='store_true')
        ]

    def run(self, verbosity, failfast, tests, ci, apponly):
        if ci:
            # Start coverage before importing, so the definitions are marked as executed
            import coverage
            cov = coverage.coverage(
                branch=True,
                omit=[
                    'templates/*',
                    'venv/*'
                ]
            )
            cov.start()

        import sys
        import glob
        import unittest

        exists = os.path.exists
        isdir = os.path.isdir
        join = os.path.join

        project_path = os.path.abspath(os.path.dirname('.'))
        sys.path.insert(0, project_path)

        # our special folder for blueprints
        if exists('apps'):
            sys.path.insert(0, join('apps'))

        loader = unittest.TestLoader()
        all_tests = []

        if not apponly:
            if exists('apps'):
                for path in glob.glob('apps/*'):
                    if isdir(path):
                        tests_dir = join(path, 'tests')

                        if exists(join(path, 'tests.py')):
                            all_tests.append(loader.discover(path, 'tests.py'))
                        elif exists(tests_dir):
                            all_tests.append(loader.discover(tests_dir, pattern=tests + '.py'))

            if exists('tests') and isdir('tests'):
                all_tests.append(loader.discover('tests', pattern=tests + '.py'))
            elif exists('tests.py'):
                all_tests.append(loader.discover('.', pattern='tests.py'))

        if 'app_path' in flask.current_app.config:
            print('Adding tests from', flask.current_app.config['app_path'])
            sys.path.insert(0, flask.current_app.config['app_path'])
            all_tests.append(loader.discover(join(flask.current_app.config['app_path'], 'tests'),
                                             pattern=tests + '.py',
                                             top_level_dir=flask.current_app.config['app_path']))

        test_suite = unittest.TestSuite(all_tests)

        if ci:
            import xmlrunner

            test_results_dir_path = os.path.join("test-results", "py")
            if not os.path.isdir(test_results_dir_path):
                os.makedirs(test_results_dir_path)

            with open(os.path.join(test_results_dir_path, "results.xml"), "wb") as output:
                result = \
                    xmlrunner.XMLTestRunner(output=output,
                                            verbosity=verbosity, failfast=failfast).run(test_suite)
                print("wrote test results to", os.path.abspath(test_results_dir_path))

                if result.wasSuccessful():
                    cov.stop()
                    cov.save()
                    coverage_html_report_dir_path = os.path.join(test_results_dir_path, "htmlcov")
                    cov.html_report(directory=coverage_html_report_dir_path)
                    cov.erase()
                    print("wrote coverage report HTML to", coverage_html_report_dir_path)
        else:
            result = \
                unittest.TextTestRunner(
                    verbosity=verbosity, failfast=failfast).run(test_suite)

        sys.exit(0 if result.wasSuccessful() else 1)
