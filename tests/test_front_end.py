from selenium import webdriver
import chromedriver_binary  # Adds chromedriver binary to path

driver = webdriver.Chrome()
#driver.get("http://www.python.org")
#assert "Python" in driver.title
driver.get("http://www.google.com")
assert 'Google' in driver.title

driver.quit()


# #from previous test code
# from selenium import webdriver
# #from selenium.webdriver.common.keys import Keys

# browser = webdriver.Firefox()

# browser.get('http://www.google.com')
# assert 'Google' in browser.title

# #elem = browser.find_element_by_name('p')  # Find the search box
# #elem.send_keys('seleniumhq' + Keys.RETURN)

# browser.quit()