import urllib2
from flask import Flask
from flask_testing import LiveServerTestCase
from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

class MyTest(LiveServerTestCase):

    def create_app(self):
        from main import app_factory
        import config
        
        #app = Flask(__name__)
        #app.config['TESTING'] = True
        # Default port is 5000
        config.Config['LIVESERVER_PORT'] = 8943
        # Default timeout is 5 seconds
        config.Config['LIVESERVER_TIMEOUT'] = 10
        application = app_factory(config.Config, config.project_name)
        
        return application

    def test_server_is_up_and_running(self):
        response = urllib2.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)

    def test_openChrome(self):
        self.driver = webdriver.Chrome()
        self.driver.get("localhost:8943")
        self.driver.quit()


# if __name__ == '__main__':
#     unittest.main()

