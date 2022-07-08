from unittest.mock import patch

from sleepy import sleep_add, sleep_multiply, sleep


@patch("time.sleep")
@patch("sleepy.sleep")
def test_sleep_mock(mock_sleep, mock_time_sleep):
    '''Test mock sleep and time.sleep'''
    sleep_add(1, 2)
    sleep_multiply(1, 2)
    mock_sleep.assert_called_with(3)
    mock_time_sleep.assert_called_with(5)