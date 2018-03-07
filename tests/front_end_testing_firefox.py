import urllib2
from flask import Flask
from flask_testing import LiveServerTestCase
from selenium import webdriver
# import chromedriver_binary  # Adds chromedriver binary to path

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

    def test_openFirefoxs(self):
        import commands
        import time
        from flask_security.utils import encrypt_password, verify_password, get_hmac
        from uuid import uuid4
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        
        #create random passord
        pw = str(uuid4())

        self.driver = webdriver.Firefox()
        self.driver.get("http://localhost:8943")
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
        time.sleep(5)
        replyButton = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote:nth-child(1) > newnanopub > button')
        replyButton.click()
        self.driver.implicitly_wait(5)
        replyAssertionTextArea = self.driver.find_element_by_css_selector('#input_30')
        replyAssertionTextArea.send_keys('Reply test')
        time.sleep(5)
        replyProvButton = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > newnanopub > md-card > md-card-title > md-nav-bar > div > nav > ul > li:nth-child(2) > button')
        replyProvButton.click()

        self.driver.find_element_by_css_selector('#input_38').send_keys('Prov reply test')
        replyButtonAdd = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > newnanopub > md-card > md-card-actions > button')
        replyButtonAdd.click()
        time.sleep(5)
        optionsReply = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > div:nth-child(5) > blockquote > div.dropdown.pull-right.ng-scope > button')
        optionsReply.click()
        self.driver.implicitly_wait(5)
        deleteReply = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > div:nth-child(5) > blockquote > div.dropdown.pull-right.ng-scope.open > ul > li:nth-child(2) > a')
        deleteReply.click()
        time.sleep(5)
        areYouSureButton = self.driver.find_element_by_css_selector('#deleteNanopubModal > div > div > div.modal-footer > button:nth-child(1)')
        areYouSureButton.click()
        # time.sleep(2)
        time.sleep(3)
        optionsButtonDropdown = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > div.dropdown.pull-right.ng-scope > button')
        optionsButtonDropdown.click()
        time.sleep(2)
        deleteButton = self.driver.find_element_by_css_selector('body > div:nth-child(4) > div > div.col-md-8 > div > div.panel-body > nanopubs > div:nth-child(4) > blockquote > div.dropdown.pull-right.ng-scope.open > ul > li:nth-child(2) > a')
        deleteButton.click()
        time.sleep(2)
        self.driver.implicitly_wait(5)
        areYouSureButton2 = self.driver.find_element_by_css_selector('#deleteNanopubModal > div > div > div.modal-footer > button:nth-child(1)')
        areYouSureButton2.click()
        time.sleep(10000)
        #to wait for response to see a
        self.driver.quit()

        
# if __name__ == '__main__':
#     unittest.main()

