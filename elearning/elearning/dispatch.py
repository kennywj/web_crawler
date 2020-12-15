#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
import signal
import random
import datetime
from threading import Timer

debug_mode = False

if debug_mode:
    SECS_PER_DAY = 120
    SECS_PER_WEEK = 120
    FULL_SECS_PER_DAY = 120
else:
    SECS_PER_DAY = 9 * 60 * 60
    SECS_PER_WEEK = 5 * SECS_PER_DAY
    FULL_SECS_PER_DAY = 24 * 60 * 60

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def empty_function(self, parameter):
    pass

class Dispatch():
    """This module generate dispatch time and hold the hook function.
    If the dispatch time is up, then it will execute the hook function.
    If there are more than one dispatch time occuring in the same time, the later
    dispatch will be discarded. The dispatch time will regenerate on the
    last dispatch.
    """

    def _cal_day_offset(self, number):
        self.day_offset = []
        day_of_now = self.now.weekday()
        # Monday is 0
        for x in range(number):
            item = self.dispatch_seconds[x]
            offset = item // SECS_PER_DAY
            if day_of_now >= 5:                # launch at weekend
                offset = (7 - day_of_now) + offset
            else:
                offset = offset + 1            # Begin from next day
                if (day_of_now + offset) >= 5: # Saturday
                    offset = offset + 2        # After Monday
            if debug_mode:
                self.day_offset.append(0)
            else:
                self.day_offset.append(offset)

    def _gen_raw_dispatch_seconds(self, number):
        self.dispatch_seconds = []
        for _ in range(number):
            time = random.randint(0, SECS_PER_WEEK)
            self.dispatch_seconds.append(time)
        self.dispatch_seconds = sorted(self.dispatch_seconds)

    def _convt_dispatch_seconds_to_base_time(self, number):
        if debug_mode:
            base_time = self.now
        else:
            base_time = datetime.datetime(self.now.year, self.now.month, self.now.day, 9, 0, 0)
        for x in range(number):
            self.dispatch_seconds[x] = base_time.timestamp() + self.dispatch_seconds[x] + \
                (self.day_offset[x] * FULL_SECS_PER_DAY)

    def _get_dispatch_seconds_within_day(self, number):
        for x in range(number):
            self.dispatch_seconds[x] = self.dispatch_seconds[x] % SECS_PER_DAY

    def gen_dispatch_timestamp(self, number):
        self.now = datetime.datetime.now()
        self._gen_raw_dispatch_seconds(number)
        self._cal_day_offset(number)
        self._get_dispatch_seconds_within_day(number)
        self._convt_dispatch_seconds_to_base_time(number)

    def show_dispatch_time(self):
        print('<< dispatch schedule >>')
        if self.number == 0:
            print('None')
            return
        for x in range(self.number):
            time = datetime.datetime.fromtimestamp(self.dispatch_seconds[x])
            print('%s, %s' % (time.strftime('%Y/%m/%d -- %H:%M:%S'), days[time.weekday()]))

    def set_dispatch_timer(self):
        if self.number == 0:
            return
        time = datetime.datetime.now().timestamp()
        bingo = False
        delta = 0
        for x in range(self.number):
            if self.dispatch_seconds[x] > time:
                delta = self.dispatch_seconds[x] - time
                bingo = True
                break
        if bingo:
            self.timer = Timer(delta, self.hook_function, args=[self])
            self.timer.daemon = True
            self.timer.start()
        else:
            self.gen_dispatch_timestamp(self.number)
            self.show_dispatch_time()
            self.set_dispatch_timer()

    def __init__(self, number=0, hook_function=None, hook_parameter=None):
        """<< parameters >>
        number        : dispatch number per week. When number is zero, it means execute hook function now
        hook_function : registered hook function which will be executed while dispatching
        hook_parameter: registered hook function's parameter
        """
        self.now = datetime.datetime.now()
        self.number = number
        if hook_function:
            self.hook_function = hook_function
        else:
            self.hook_function = empty_function
        self.hook_parameter = hook_parameter
        if number == 0:
            self.hook_function(self)
        else:
            self.gen_dispatch_timestamp(number)
            self.show_dispatch_time()
            self.set_dispatch_timer()

def main_dummy(self):
    print(self.hook_parameter)
    time = datetime.datetime.now()
    print('%s, %s' % (time.strftime('%Y/%m/%d -- %H:%M:%S'), days[time.weekday()]))
    self.set_dispatch_timer()

def main_dummy_once(self):
    print(self.hook_parameter)
    time = datetime.datetime.now()
    print('%s, %s' % (time.strftime('%Y/%m/%d -- %H:%M:%S'), days[time.weekday()]))

def main_sig_handler(sig, frame):
    print('Got signal to exit')
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, main_sig_handler)
    if len(sys.argv) == 1:
        number = 0
        dispatch = Dispatch(number, main_dummy_once, '<< dispatch occurrence >>')
    else:
        number = int(sys.argv[1])
        dispatch = Dispatch(number, main_dummy, '<< dispatch occurrence >>')
    while True:
        time.sleep(10)
