start_value = 76.32 - 0.1
def side_effect(*arhs, **kwargs):
    nonlocal start_value
    start_value += 0.1
    return start_value
mock_get_usd_course.side_effect = side_effect