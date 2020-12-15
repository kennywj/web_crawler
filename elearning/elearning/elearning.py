#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import datetime
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_ELEARNING = 'http://issbg.efoxconn.com/semielearning/#/login'

class ELearning():
    """This module provides auto-display elearning web page function.
    """

    def __init__(self, username, password, max_window=True, video_timeout=0, change_page_time=1):
        """[ parameters ]
        username         : user name for the web page
        password         : user password for the web page
        max_window       : maximum window or minimum window
        video_timeout    : maximum video playback time (seconds)
        change_page_time : time for change page (seconds)
        """
        self.username = username
        self.password = password
        self.max_window = max_window
        self.delay = 5
        self.video_timeout = video_timeout
        self.change_page_time = change_page_time
        self._init_variables()

    def _init_variables(self):
        self.counter = 0
        self.driver = None
        self.wait = None
        self.num_category = 0
        self.index_category = 0
        self.category = None
        self.num_topic = 0
        self.index_topic = 0
        self.topic = None

    def select_category(self):
        self.category = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'category-title')))
        self.category = self.driver.find_elements_by_class_name('category-title')
        self.num_category = len(self.category)
        assert self.num_category > 0
        # avoid all category
        self.index_category = random.randint(1, self.num_category - 1)
        element = self.category[self.index_category]
        element.click()
        # if we don't sleep here, we will read the previous total-results
        time.sleep(5)
        item = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'total-results')))
        self.num_topic = int(re.findall(r'\d+', item.text)[2])
        assert self.num_topic > 0
        print('[ select category: %s with %d items ]' % (element.text, self.num_topic))

    def _select_tab(self, index):
        x = 0
        while x < index:
            element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-next")))
            element.click()
            x = x + 1

    def select_topic(self):
        self.index_topic = random.randint(0, self.num_topic - 1)
        self._select_tab(self.index_topic // 10)
        topic_xpath = '//div[@class="el-table__body-wrapper"]/table/tbody/tr[{}]/td[1]'.format((self.index_topic % 10) + 1)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, topic_xpath)))
        element.click()
        print('[ select topic: %s (%d) ]' % (element.text, self.index_topic))

    def _play_document(self, number):
        element = self.driver.find_element_by_class_name('content-container')
        focus = ActionChains(self.driver).move_to_element(element).click()
        focus.perform()
        html = self.driver.find_element_by_tag_name('html')
        number = number + (number // 2)
        for _ in range(number):
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(self.change_page_time)
        html.send_keys(Keys.END)
        time.sleep(self.change_page_time)
        html.send_keys(Keys.END)
        time.sleep(self.change_page_time)

    def _play_video(self):
        begin = datetime.datetime.now().timestamp()
        while True:
            element = self.driver.find_element_by_xpath("//span[@class='vjs-remaining-time-display']")
            if element.text == '-0:00':
                break
            time.sleep(5)
            if self.video_timeout > 0:
                if (datetime.datetime.now().timestamp() - begin) > self.video_timeout:
                    break

    def play(self):
        items = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'info-card-file')))
        items = self.driver.find_elements_by_class_name('info-card-file')
        num_item = len(items)
        for index in range(num_item):
            item = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'info-card-file')))
            item = self.driver.find_elements_by_class_name('info-card-file')[index]
            print('[ play start: %s ]' % item.text)
            item.click()
            time.sleep(5)
            try:
                element = self.driver.find_element_by_xpath('//*[@id="buttons"]/a')
                num_page = int(re.findall(r'\d+', element.text)[1])
                print('type document: %s pages' % num_page)
                self._play_document(num_page)
            except NoSuchElementException:
                print('type video')
                self._play_video()
            print('[ play end ]')
            self._previous_page()
        self._previous_page()

    def _previous_page(self):
        element = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'back-title')))
        element.click()
        time.sleep(1)

    def open(self):
        self.driver = webdriver.Chrome()
        if self.max_window:
            self.driver.maximize_window()
        else:
            self.driver.minimize_window()
        self.driver.get(URL_ELEARNING)
        self.wait = WebDriverWait(self.driver, 10)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='帳號']")))
        element.send_keys(self.username)
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密碼']")))
        element.send_keys(self.password)

        button = None
        buttons = self.driver.find_elements_by_css_selector("button")
        for btn in buttons:
            if btn.text == '登入':
                button = btn
        button.click()

    def close(self):
        element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.el-dropdown-link')))
        focus = ActionChains(self.driver).move_to_element(element).click()
        focus.perform()
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.el-dropdown-menu__item:nth-child(2)')))
            element.click()
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='el-message-box__btns']/button[2]")))
            element.click()
        except (ElementNotInteractableException, TimeoutException):
            print('Close page without logout.')
        self.driver.close()
        self.driver = None

if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.exit()
    username = sys.argv[1]
    password = sys.argv[2]
    number = int(sys.argv[3])
    max_window = True
    video_timeout = int(sys.argv[4])
    change_page_time = int(sys.argv[5])
    web = ELearning(username, password, max_window, video_timeout, change_page_time)
    web.open()
    for _ in range(number):
        web.select_category()
        web.select_topic()
        web.play()
    time.sleep(3)
    web.close()
    print('bye bye')
