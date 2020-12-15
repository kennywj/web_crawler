#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, getopt
import time
import datetime
import signal
from elearning.elearning import ELearning
from elearning.dispatch import Dispatch, days
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, TimeoutException, NoSuchElementException

def main_sig_handler(sig, frame):
    print('Got signal to exit')
    sys.exit()

signal.signal(signal.SIGINT, main_sig_handler)

help_string = 'Usage: %s [option] <parameter>\nThe option and option\'s parameter list below:\n' \
    'Ex:\n' \
    '\t%s -u xxx -p yyy\n\n' \
    '-u <username>\n' \
    '\t[ default value: None ]\n' \
    '\tUser name for the web site.\n' \
    '-p <password>\n' \
    '\t[ default value: None ]\n' \
    '\tUser password for the web site.\n' \
    '-f <frequency>\n' \
    '\t[ default value: 0 ]\n' \
    '\tAuto play times per week.\n\t0 means auto play now without scheduler.\n' \
    '-n <number>\n' \
    '\t[ default value: 1 ]\n' \
    '\tAuto play topic number per time.\n' \
    '-t <timeout>\n' \
    '\t[ default value: 0 ]\n' \
    '\tTime out (seconds) for the video.\n\t0 means waiting for the video finished.\n' \
    '-d <delay>\n' \
    '\t[ default value: 1 ]\n' \
    '\tChange page delay (seconds) for the document.\n'

def usage():
    print(help_string % (sys.argv[0], sys.argv[0]))

def play(self):
    print('<< dispatch occurrence >>')
    time = datetime.datetime.now()
    print('%s, %s' % (time.strftime('%Y/%m/%d -- %H:%M:%S'), days[time.weekday()]))
    config = self.hook_parameter
    web = ELearning(config['username'], config['password'], True, \
        config['timeout'], config['delay'])

    try:
        web.open()

        for _ in range(config['number']):
            web.select_category()
            web.select_topic()
            web.play()

        web.close()
    except (ElementNotInteractableException, TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        print('User interrupt or web site is busy!!!')
        print('Reschedule next time!!!')
    print('bye bye')
    self.set_dispatch_timer()

def main(argv):
    config = {}
    try:
        opts, _ = getopt.getopt(argv, "hu:p:f:n:t:d:", \
            ["username=","password=","frequency=","number=","timeout=","delay="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    config['username'] = None
    config['password'] = None
    config['frequency'] = 0
    config['number'] = 1
    config['timeout'] = 0
    config['delay'] = 1

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-u", "--username"):
            config['username'] = arg
        elif opt in ("-p", "--password"):
            config['password'] = arg
        elif opt in ("-f", "--frequency"):
            config['frequency'] = int(arg)
        elif opt in ("-n", "--number"):
            config['number'] = int(arg)
        elif opt in ("-t", "--timeout"):
            config['timeout'] = int(arg)
        elif opt in ("-d", "--delay"):
            config['delay'] = int(arg)
    if not config['username'] or not config['password']:
        usage()
        sys.exit(2)

    for key in config:
        print('key:', key)
        print('value: %s' % str(config[key]))

    _unused_dispatch = Dispatch(config['frequency'], play, config)

    if config['frequency'] != 0:
        while True:
            time.sleep(100)

if __name__ == "__main__":
    main(sys.argv[1:])
