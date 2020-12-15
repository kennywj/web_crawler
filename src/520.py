from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import argparse
import time

#
# start main program
#
def main():
	parser = argparse.ArgumentParser(description="The program will do sogo web crawler.")
	parser.add_argument("username",help="login sogo user name")
	parser.add_argument("password",help="login sog password")
	args = parser.parse_args()
	
	options = Options()
	options.add_argument("--disable-notifications")
 
	chrome = webdriver.Chrome('./chromedriver', chrome_options=options)
	chrome.get("https://www.520cc.cc/agree.php?referer=%2Fforum.php")
	time.sleep(2)

	#username = chrome.find_element_by_name("username")
	username = chrome.find_element_by_xpath("//input[@type='text' and @name='username']")
	username.send_keys(args.username)

	#password = chrome.find_element_by_name("password")
	password = chrome.find_element_by_xpath("//input[@type='password' and @name='password']")
	password.send_keys(args.password)

	buttons = chrome.find_elements_by_name("loginsubmit")
	for btn in buttons:
		if btn.text == '登入':
			button = btn
	button.click()

	time.sleep(2)
	return

if __name__ == '__main__':
	main()