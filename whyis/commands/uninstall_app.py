import subprocess
import ast
import logging
import os.path

from flask_script import Command, Option


class UninstallApp(Command):
    """
    Uninstall the current whyis application.
    """

    def get_options(self):
        return [
            Option('-y', '--yes', dest='yes', action='store_true', help='Respond to all prompts with "yes"', default=False)
        ]


    def run(self, yes: bool):
        try:
            import config
        except ImportError:
            logging.warning("unable to import config; no application installed?")
            return

        app_dir_path = os.path.dirname(config.__file__)
        setup_py_file_path = os.path.join(app_dir_path, "setup.py")
        if not os.path.isfile(setup_py_file_path):
            logging.warning("%s does not exist")
            return

        project_name = None
        with open(setup_py_file_path) as setup_py_file:
            ast_ = ast.parse(setup_py_file.read(), setup_py_file.name)

            class SetupNodeVisitor(ast.NodeVisitor):
                def __init__(self):
                    ast.NodeVisitor.__init__(self)
                    self.project_name = None

                def visit(self, node):
                    if isinstance(node, ast.Call):
                        call_node = node
                        if hasattr(call_node, "func") and call_node.func.id == "setup" and hasattr(call_node, "keywords"):
                            for keyword_node in call_node.keywords:
                                if keyword_node.arg == "name" and isinstance(keyword_node.value, ast.Str):
                                    self.project_name = keyword_node.value.s
                                    break

                    self.generic_visit(node)
            visitor = SetupNodeVisitor()
            visitor.visit(ast_)
            project_name = visitor.project_name
        if project_name is None:
            logging.warning("unable to parse project name from setup.py")
            return
        project_id = project_name.replace(" ", "-")
        logging.info("App project: %s (%s)", project_name, project_id)

        pip_args = ["pip", "uninstall"]
        if yes:
            pip_args.append("-y")
        pip_args.append(project_id)
        logging.info(" ".join(pip_args))
        subprocess.call(pip_args)
