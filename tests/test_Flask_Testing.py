import urllib2
from flask import Flask
from flask_testing import LiveServerTestCase
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

class MyTest(LiveServerTestCase):

    def create_app(self):
        from main import app_factory
        from depot.manager import DepotManager
        import config_defaults
        
        #app = Flask(__name__)
        #app.config['TESTING'] = True
        # Default port is 5000
        config_defaults.Config['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        config_defaults.Config['LIVESERVER_TIMEOUT'] = 10
        
        application = app_factory(config_defaults.Config, config_defaults.project_name)
        
        return application

    def test_server_is_up_and_running(self):
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_openChrome(self):
        #not going to use config.json file
        # import json
        # with open('./tests/config.json') as f:
        #     configFile = json.load(f)
        # from commands import CreateUser, rando
        import commands
        from flask_security.utils import encrypt_password, verify_password, get_hmac
        from uuid import uuid4
        #create random passord
        pw = str(uuid4())

        self.driver = webdriver.Chrome()
        self.driver.get("localhost:8943")
        creator = commands.CreateUser()
        creator.run('user@example.com', pw, 'First', 'Last', 'identifier', '--roles=admin')
        
        elem = self.driver.find_element_by_id('email')
        elem.send_keys('user@example.com')
        pw_elem = self.driver.find_element_by_id('password')
        pw_elem.send_keys(pw)
        self.driver.find_element_by_id('submit').click()
        self.driver.save_screenshot('/apps/Downloads/screenshot.png')
        self.driver.implicitly_wait(20) # seconds
        self.driver.find_element_by_link_text('Add...').click()


        #self.driver.quit()


# if __name__ == '__main__':
#     unittest.main()

