#from previous test code
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox()

browser.get('http://www.google.com')
assert 'Google' in browser.title

elem = browser.find_element_by_id('lst-ib')  # Find the search box
elem.send_keys('seleniumhq' + Keys.RETURN)


browser.quit()