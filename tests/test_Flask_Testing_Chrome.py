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
        import commands
        import time
        from flask_security.utils import encrypt_password, verify_password, get_hmac
        from uuid import uuid4
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
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
        self.driver.implicitly_wait(5) # seconds
        #find Add... button
        self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > newnanopub > button').click()
        self.driver.implicitly_wait(10) # seconds
        assertionTextArea = self.driver.find_element_by_css_selector('#input_1')
        assertionTextArea.send_keys('This is a test')
        self.driver.save_screenshot('/apps/Downloads/assert-screenshot.png')
        provButton = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > newnanopub > md-card > md-card-title > md-nav-bar > div > nav > ul > li:nth-child(2) > button')
        provButton.click()
        #find prov text area
        provTextArea = self.driver.find_element_by_css_selector('#input_9')
        provTextArea.send_keys('Prov test')
        self.driver.save_screenshot('/apps/Downloads/prov-screenshot.png')
        #find Add button to save both prov and assertion
        addButton =  self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > newnanopub > md-card > md-card-actions > button')
        self.driver.implicitly_wait(5)        
        addButton.click()
        self.driver.maximize_window()
        #to wait for response to see addition
        time.sleep(10)
        self.driver.quit()

        
# if __name__ == '__main__':
#     unittest.main()

