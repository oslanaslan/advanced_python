'''
Tests for module task_Ashabokov_Aslan_web_spy
'''

from unittest import mock
from argparse import Namespace, ArgumentParser

import pytest

from task_Ashabokov_Aslan_web_spy import main, get_html, \
    parse_html, setup_parser, gitlab_parser_callback


GITLAB_URL = 'https://about.gitlab.com/features/'
HTML_DUMP_FILEPATH = 'gitlab_features.html'
EXPECTED_HTML_DUMP = 'gitlab_features_expected.html'
FREE_IN_TEST_FILE = 351
NON_FREE_IN_TEST_FILE = 218


@pytest.mark.slow
def test_setup_parser():
    '''Test parser setup function'''
    parser = setup_parser()
    assert isinstance(parser, ArgumentParser)

@pytest.mark.slow
@mock.patch("task_Ashabokov_Aslan_web_spy.get_html")
@mock.patch("task_Ashabokov_Aslan_web_spy.print")
@mock.patch("task_Ashabokov_Aslan_web_spy.ArgumentParser.parse_args")
def test_main(mock_parse_args, mock_print, mock_get_html):
    '''Test main function'''
    mock_parse_args.return_value = Namespace(
        command='gitlab',
        url=GITLAB_URL,
        callback=gitlab_parser_callback,
    )
    mock_print.return_value = None
    with open(HTML_DUMP_FILEPATH, 'r') as fin:
        html_dump = fin.read()
    mock_get_html.return_value = html_dump
    main()

@pytest.mark.slow
@mock.patch("requests.get")
def test_get_html_local(mock_get):
    '''Test get_html function locally'''

    with open(HTML_DUMP_FILEPATH, 'r') as fin:
        html_dump = fin.read()

    mock_get.return_value = Namespace(text=html_dump)
    get_html_result = get_html(GITLAB_URL)

    assert html_dump == get_html_result, \
            (f'get_html response should match to {HTML_DUMP_FILEPATH} file')

@pytest.mark.slow
@mock.patch('task_Ashabokov_Aslan_web_spy.get_html')
def test_parse_html_local(mock_get_html):
    '''Test html parsing'''

    with open(HTML_DUMP_FILEPATH, 'r') as fin:
        html_dump = fin.read()

    mock_get_html.return_value = html_dump
    free_count, non_free_count = parse_html(GITLAB_URL)

    assert FREE_IN_TEST_FILE == free_count, \
        (f'True FREE count: {FREE_IN_TEST_FILE}. Got: {free_count}.')
    assert NON_FREE_IN_TEST_FILE == non_free_count, \
        (f'True non FREE count: {NON_FREE_IN_TEST_FILE}. Got: {non_free_count}.')

@pytest.mark.integration_test
def test_compare_dump_html_and_web_html():
    '''Compare if web html coresponds to data from dump'''

    with open(EXPECTED_HTML_DUMP, 'r') as fin:
        html_dump = fin.read()

    with mock.patch("task_Ashabokov_Aslan_web_spy.get_html") as mock_get_html:
        mock_get_html.return_value = html_dump
        true_free_count, true_non_free_count = parse_html(GITLAB_URL)

    loaded_free_count, loaded_non_free_count = parse_html(GITLAB_URL)

    assert true_free_count == loaded_free_count and \
        true_non_free_count == loaded_non_free_count, (
            f"expected free product count is {true_free_count}, while you calculated {loaded_free_count}; expected enterprise product count is {true_non_free_count}, while you calculated {loaded_non_free_count}"
        )
