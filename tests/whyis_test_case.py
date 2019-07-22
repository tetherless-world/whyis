from flask_testing import TestCase


class WhyisTestCase(TestCase):

    def create_app(self):
        from main import app_factory
        from depot.manager import DepotManager
        import config_defaults

        if 'admin_queryEndpoint' in config_defaults.Test:
            del config_defaults.Test['admin_queryEndpoint']
            del config_defaults.Test['admin_updateEndpoint']
            del config_defaults.Test['knowledge_queryEndpoint']
            del config_defaults.Test['knowledge_updateEndpoint']

        # Default port is 5000
        config_defaults.Test['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        config_defaults.Test['LIVESERVER_TIMEOUT'] = 10

        application = app_factory(config_defaults.Test, config_defaults.project_name)
        application.config['TESTING'] = True
        application.config['WTF_CSRF_ENABLED'] = False

        return application

    def create_user(self, email, password, username="identifier", fn="First", ln="Last", roles='Admin'):
        import commands
        from uuid import uuid4
        pw = 'password'
        creator = commands.CreateUser()
        creator.run(email, password, fn, ln, username, roles)
        return email, password

    def login(self, email, password):
        return self.client.post('/login', data={'email': email, 'password': password, 'remember': 'y'},
                                follow_redirects=True)

