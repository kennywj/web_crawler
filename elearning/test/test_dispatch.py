import pytest
import datetime
import time
import random
from elearning.dispatch import Dispatch, days

original_value = 10

def hook_modify_value_once(self):
    self.hook_parameter[0] = self.hook_parameter[0] + 1
    print('<< dispatch occurrence >>')
    time = datetime.datetime.now()
    print('%s, %s' % (time.strftime('%Y/%m/%d -- %H:%M:%S'), days[time.weekday()]))

def hook_modify_value_schedule(self):
    hook_modify_value_once(self)
    self.set_dispatch_timer()

def test_run_once():
    value = [original_value]
    _unused_scheduler = Dispatch(0, hook_modify_value_once, value)
    assert value[0] == original_value + 1

def test_dispatch_after_execution(monkeypatch):
    value = [original_value]
    def mock_gen_dispatch_timestamp(self, *args, **kwargs):
        exec_time = datetime.datetime.now().timestamp() + 3
        self.dispatch_seconds = [exec_time]
    monkeypatch.setattr(Dispatch, 'gen_dispatch_timestamp', mock_gen_dispatch_timestamp)
    _unused_scheduler = Dispatch(1, hook_modify_value_once, value)
    time.sleep(3 + 1)
    assert value[0] == original_value + 1

def test_dispatch_before_execution(monkeypatch):
    value = [original_value]
    def mock_gen_dispatch_timestamp(self, *args, **kwargs):
        exec_time = datetime.datetime.now().timestamp() + 3
        self.dispatch_seconds = [exec_time]
    monkeypatch.setattr(Dispatch, 'gen_dispatch_timestamp', mock_gen_dispatch_timestamp)
    _unused_scheduler = Dispatch(1, hook_modify_value_once, value)
    time.sleep(3 - 2)
    assert value[0] == original_value

def test_dispatch_twice(monkeypatch):
    value = [original_value]
    def mock_gen_dispatch_timestamp(self, *args, **kwargs):
        exec_time = datetime.datetime.now().timestamp() + 3
        self.dispatch_seconds = [exec_time, exec_time + 3]
    monkeypatch.setattr(Dispatch, 'gen_dispatch_timestamp', mock_gen_dispatch_timestamp)
    _unused_scheduler = Dispatch(2, hook_modify_value_schedule, value)
    time.sleep(6 + 2)
    assert value[0] == original_value + 2

# Tuesday
FAKE_TIME_NOW = None

@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return FAKE_TIME_NOW

    monkeypatch.setattr(datetime, 'datetime', mydatetime)

@pytest.fixture
def setup_dispatch_time(patch_datetime_now, monkeypatch):
    def _func_body(now, offset):
        global FAKE_TIME_NOW
        FAKE_TIME_NOW = now
        def mock_randint(self, *args, **kwargs):
            return offset
        monkeypatch.setattr(random, 'randint', mock_randint)
        def mock_set_dispatch_timer(self, *args, **kwargs):
            pass
        monkeypatch.setattr(Dispatch, 'set_dispatch_timer', mock_set_dispatch_timer)
        return

    return _func_body

def test_dispatch_on_thursday(setup_dispatch_time):
    # Arrange
    thursday = datetime.datetime(2020, 10, 29, 9, 0, 0)
    offset_smaller_than_one_day = (9 * 60 * 60) - 1
    setup_dispatch_time(thursday, offset_smaller_than_one_day)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on friday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 10, 30, 17, 59, 59).timestamp()

def test_dispatch_on_friday(setup_dispatch_time):
    # Arrange
    thursday = datetime.datetime(2020, 10, 29, 9, 0, 0)
    offset_bigger_than_one_day = (9 * 60 * 60)
    setup_dispatch_time(thursday, offset_bigger_than_one_day)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on monday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 11, 2, 9, 0, 0).timestamp()

def test_dispatch_on_saturday(setup_dispatch_time):
    # Arrange
    thursday = datetime.datetime(2020, 10, 29, 9, 0, 0)
    offset_smaller_than_one_day = (2 * 9 * 60 * 60)
    setup_dispatch_time(thursday, offset_smaller_than_one_day)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on tuesday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 11, 3, 9, 0, 0).timestamp()

def test_dispatch_on_next_monday(setup_dispatch_time):
    # Arrange
    thursday = datetime.datetime(2020, 10, 29, 9, 0, 0)
    offset_smaller_than_one_day = (4 * 9 * 60 * 60)
    setup_dispatch_time(thursday, offset_smaller_than_one_day)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on thursday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 11, 5, 9, 0, 0).timestamp()

def test_launch_on_thursday_night(setup_dispatch_time):
    # Arrange
    thursday = datetime.datetime(2020, 10, 29, 19, 30, 0)
    offset = (1 * 60 * 60)
    setup_dispatch_time(thursday, offset)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on friday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 10, 30, 10, 0, 0).timestamp()

def test_launch_on_saturday(setup_dispatch_time):
    # Arrange
    saturday = datetime.datetime(2020, 10, 31, 12, 30, 0)
    offset = (1 * 60 * 60)
    setup_dispatch_time(saturday, offset)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on monday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 11, 2, 10, 0, 0).timestamp()


def test_launch_on_sunday(setup_dispatch_time):
    # Arrange
    sunday = datetime.datetime(2020, 11, 1, 12, 30, 0)
    offset = (1 * 60 * 60)
    setup_dispatch_time(sunday, offset)
    value = [original_value]
    # Act
    scheduler = Dispatch(1, hook_modify_value_once, value)
    # Assert
    # dispatch on monday
    assert scheduler.dispatch_seconds[0] == datetime.datetime(2020, 11, 2, 10, 0, 0).timestamp()
