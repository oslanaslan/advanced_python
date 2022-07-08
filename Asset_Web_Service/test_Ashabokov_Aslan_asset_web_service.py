'''
Test task_Ashabokov_Aslan_asset_web_service module
'''
from unittest import mock
from argparse import ArgumentParser, Namespace
import json

import requests
import pytest

from task_Ashabokov_Aslan_asset_web_service import (
    Asset,
    app,
    load_asset_from_file,
    print_asset_revenue,
    setup_parser,
    parse_cbr_currency_base_daily,
    parse_cbr_key_indicators,
    API_CBR_DAILY,
    API_CBR_KEY_INDICATORS,
    API_503_MESSAGE,
    API_404_MESSAGE,
    API_ASSET_LIST,
    API_GET_ASSET,
    API_CALCULATE_REVENUE,
    API_CLEANUP,
)


# Parser tests

EPS = 10e-8
TEST_ASSET_FILE = "test_asset.txt"
CBR_DAILY_HTML = "cbr_currency_base_daily.html"
CBR_KEY_INDICATORS_HTML = "cbr_key_indicators.html"
API_UNKNOWN_ROUTE = "abc/gg/wp"

def test_parse_cbr_currency_base_daily():
    '''Test parse_cbr_currency_base_daily'''
    with open(CBR_DAILY_HTML) as fin:
        html_dump = fin.read()

    result_dict = parse_cbr_currency_base_daily(html_dump)
    aud_rate = result_dict['AUD']
    amd_rate = result_dict['AMD']

    assert len(result_dict) == 34, (
        f'result_dict should contain 35 items.\nGot: {len(result_dict)}'
    )
    assert abs(aud_rate - 57.0229) < EPS, (
        f"AUD value should be: 57.0229.\nGot: {aud_rate}"
    )
    assert abs(amd_rate - 14.4485 / 100) < EPS, (
        f"AMD value should be: {14.4485 / 100}.\nGot: {amd_rate}"
    )

def test_parse_cbr_key_indicators():
    '''Test parse_cbr_key_indicators'''
    with open(CBR_KEY_INDICATORS_HTML) as fin:
        html_dump = fin.read()

    result_dict = parse_cbr_key_indicators(html_dump)

    for tag in result_dict:
        assert isinstance(result_dict[tag], float), (
            f"Value should type of float.\nGot: {type(result_dict[tag])}"
        )

# API tests

@pytest.fixture
def client():
    '''Get flask client fixture'''
    with app.test_client() as client:
        yield client

@mock.patch("requests.get")
def test_local_cbr_daily_callback(mock_get, client):
    '''Test local cbr_daily_callback'''
    with open(CBR_DAILY_HTML) as fin:
        html_dump = fin.read()
    response = Namespace()
    response.status_code = 200
    response.text = html_dump
    response.ok = True
    mock_get.return_value = response
    client_response = client.get(API_CBR_DAILY)

    assert client_response.status_code == 200, (
        f"Status code should be 200.\nGot: {client_response.status_code}"
    )
    amd_rate = json.loads(client_response.data)['AMD']
    current_amd_rate = 0.144485
    assert abs(current_amd_rate - amd_rate) < EPS, (
        f"AMD rate should be: 0.144485.\nGot: {amd_rate}"
    )

def test_cbr_daily_callback(client):
    '''Test cbr_daily_callback with real request'''
    response = client.get(API_CBR_DAILY)

    assert response.status_code == 200, (
        f"Status code should be 200.\nGot: {response.status_code}"
    )
    assert response.content_type == "application/json", (
        f"Content type should be application/json.\nGot: {response.content_type}"
    )
    assert response.is_json, (
        "Response should be json."
    )

@mock.patch("requests.get")
def test_local_cbr_indicators_callback(mock_get, client):
    '''Test local cbr_indicators_callback'''
    with open(CBR_KEY_INDICATORS_HTML) as fin:
        html_dump = fin.read()
    response = Namespace()
    response.status_code = 200
    response.text = html_dump
    response.ok = True
    mock_get.return_value = response
    client_response = client.get(API_CBR_KEY_INDICATORS)

    assert client_response.status_code == 200, (
        f"Status code should be 200.\nGot: {client_response.status_code}"
    )

def test_cbr_indicators_callback(client):
    '''Test cbr_indicators_callback with real request'''
    response = client.get(API_CBR_KEY_INDICATORS)

    assert response.status_code == 200, (
        f"Status code should be 200.\nGot: {response.status_code}"
    )
    assert response.content_type == "application/json", (
        f"Content type should be application/json.\nGot: {response.content_type}"
    )

def test_page_not_found(client):
    '''Test 404 error'''
    response = client.get(API_UNKNOWN_ROUTE)
    assert response.status_code == 404, (
        f"Status code should be 404.\nGot: {response.status_code}"
    )
    assert not response.is_json, (
        "Error response should not be json."
    )
    assert API_404_MESSAGE in response.get_data().decode(), (
        f"Text should be: {API_404_MESSAGE}.\nGot: {response.get_data().decode()}"
    )

@mock.patch("requests.get")
def test_page_is_not_accessable(mock_get, client):
    '''Test error 503'''

    def lambda_function(x):
        raise requests.exceptions.ConnectionError()

    true_state_code = 503
    mock_get.side_effect = lambda_function
    response = client.get(API_CBR_DAILY)

    assert response.status_code == true_state_code, (
        f"Status code should be {true_state_code}.\nGot: {response.status_code}"
    )
    assert API_503_MESSAGE == response.get_data().decode(), (
        f"Response message should be: {API_503_MESSAGE}.\nGot: {response.get_data().decode()}"
    )

def create_test_asset_url(
        name: str = None,
        char_code: str = None,
        capital: float = None,
        interest: float = None
    ) -> str:
    '''Create URL for adding test asset'''
    name = name or "MyAsset"
    char_code = char_code or'USD'
    capital = capital or 1
    interest = interest or 0.5
    request_url = f"/api/asset/add/{char_code}/{name}/{capital}/{interest}"

    return request_url

def create_test_asset_get_url(
        name_1: str = None,
        name_2: str = None,
    ):
    '''Help function for testing get asset callback'''
    name_1 = name_1 or "MyAsset1"
    name_2 = name_2 or "MyAsset2"
    request_url = API_GET_ASSET + f"?name={name_1}&name={name_2}"

    return request_url

def create_test_revenue_request_url(periods: str = None):
    '''Help function for create calculate_revenue request'''
    periods = periods or [5, 10]
    request_url = API_CALCULATE_REVENUE + "?"

    for period in periods:
        request_url += f"period={period}&"

    if len(periods) != 0:
        request_url = request_url[:-1]

    return request_url

def test_create_asset_callback(client):
    '''Test create_asset_callback'''
    name = "MyAsset"
    request_url = create_test_asset_url(name)
    response = client.get(request_url)

    status_code = 200
    msg = f"Asset {name} was successfully added"

    assert status_code == response.status_code, (
        f"Status code should be: {status_code}.\nGot: {response.status_code}"
    )
    assert not response.is_json, (
        "Response should be text."
    )
    response_text = response.get_data().decode()
    target_text = msg.format(name)
    assert target_text == response_text, (
        f"Response should be: {response_text}.\nGot: {target_text}"
    )

    status_code = 403
    msg = f"Asset {name} already exists"
    response = client.get(request_url)

    assert status_code == response.status_code, (
        f"Status code should be: {status_code}.\nGot: {response.status_code}"
    )
    assert not response.is_json, (
        "Response should be text."
    )
    response_text = response.get_data().decode()
    target_text = msg.format(name)
    assert target_text == response_text, (
        f"Response should be: {response_text}.\nGot: {target_text}"
    )

def test_get_asset_list_callback(client):
    '''Test load_asset_from_file'''
    first_asset_name = "MyAsset1"
    second_asset_name = "MyAsset2"
    add_asset_1_url = create_test_asset_url(first_asset_name)
    add_asset_2_url = create_test_asset_url(second_asset_name)
    response = client.get(add_asset_2_url)

    assert response.status_code == 200, (
        "Status code must be 200."
    )
    response = client.get(add_asset_1_url)
    assert response.status_code == 200, (
        "Status code must be 200."
    )
    response = client.get(API_ASSET_LIST)

    assert response.status_code == 200, (
        "Status code must be 200."
    )
    assert response.is_json, (
        "Response must be json."
    )

    res_lst = json.loads(response.get_data())

    assert len(res_lst) == 3, (
        f"Response len must be 2.\nGot: {len(res_lst)}"
    )
    assert first_asset_name == res_lst[1][1], (
        f"Asset {first_asset_name} must be first.\nGot: {res_lst}"
    )

def test_get_asset_callback(client):
    '''Test get_asset_callback'''
    request_url = create_test_asset_get_url()
    response = client.get(request_url)

    # from pdb import set_trace; set_trace();

    assert response.status_code == 200, (
        "Status code must be 200."
    )

    res_lst = json.loads(response.get_data())

    assert len(res_lst) == 2, (
        f"Response len must be 2.\nGot: {len(res_lst)}"
    )
    assert res_lst[1][1] == "MyAsset2", (
        f"Asset MyAsset2 must be first.\nGot: {res_lst}"
    )

def test_cleanup_callback(client):
    '''Test cleanup_callback'''
    response = client.get(API_CLEANUP)
    true_msg = "there are no more assets"
    response_msg = response.get_data().decode()

    assert response.status_code == 200, (
        f"Status code must be 200.\nGot: {response.status_code}"
    )
    assert true_msg == response_msg, (
        f"Msg must be: {true_msg}.\nGot: {response_msg}"
    )

    response = client.get(API_ASSET_LIST)

    assert response.status_code == 200, (
        f"Status code must be 200.\nGot: {response.status_code}"
    )
    res_lst = json.loads(response.get_data().decode())
    assert len(res_lst) == 0, (
        f"Must return empty list.\nGot: {res_lst}"
    )

def test_calculate_revenue_callback(client):
    '''Test calculate_revenue_callback'''
    revenue_request_url = create_test_revenue_request_url(
        [1]
    )
    add_first_asset_url = create_test_asset_url(
        name="T1",
        char_code="RUB",
        capital=100,
        interest=0.1,
    )
    add_second_asset_url = create_test_asset_url(
        name="T2",
        char_code="RUB",
        capital=100,
        interest=0.1,
    )

    response = client.get(add_first_asset_url)

    assert response.status_code == 200, (
        f"Status code must be 200,\nGot: {response.status_code}"
    )

    response = client.get(add_second_asset_url)

    assert response.status_code == 200, (
        f"Status code must be 200,\nGot: {response.status_code}"
    )

    response = client.get(revenue_request_url)

    assert response.status_code == 200, (
        f"Response status code must be 200.\nGot: {response.status_code}"
    )

    res_dict = json.loads(response.get_data())
    expected_revenue = 20.000000000000018

    assert abs(res_dict["1"] - expected_revenue) < EPS, (
        f"Expected revenue: {expected_revenue}.\nGot: {res_dict['1']}"
    )

    add_asset_url = create_test_asset_url(
        name="T3",
        char_code="USD",
        capital=100,
        interest=0.1,
    )
    response = client.get(add_asset_url)

    assert response.status_code == 200, (
        f"Response status code must be 200.\nGot: {response.status_code}"
    )

    add_asset_url = create_test_asset_url(
        name="T4",
        char_code="AMD",
        capital=10,
        interest=0.1,
    )
    response = client.get(add_asset_url)

    assert response.status_code == 200, (
        f"Response status code must be 200.\nGot: {response.status_code}"
    )

    add_asset_url = create_test_asset_url(
        name="T5",
        char_code="Au",
        capital=50,
        interest=0.1,
    )
    response = client.get(add_asset_url)

    assert response.status_code == 200, (
        f"Response status code must be 200.\nGot: {response.status_code}"
    )

    revenue_request_url = create_test_revenue_request_url([1, 2])
    response = client.get(revenue_request_url)

    assert response.status_code == 200, (
        f"Response status code must be 200.\nGot: {response.status_code}"
    )

    res_dict = json.loads(response.get_data())
    expected_revenue = 21805.34615400002

    assert abs(res_dict["1"] - expected_revenue) < EPS, (
        f"Expected revenue: {expected_revenue}.\nGot: {res_dict['1']}"
    )

    expected_revenue = 45791.22692340005

    assert abs(res_dict["2"] - expected_revenue) < EPS, (
        f"Expected revenue: {expected_revenue}.\nGot: {res_dict['2']}"
    )

# Test Asset class

def test_build_from_str():
    '''Test build from str'''
    asset_str = "MyAsset 1 0.1"
    asset_1 = Asset.build_from_str(asset_str)
    asset_2 = Asset(
        name="MyAsset",
        capital=1,
        interest=0.1
    )
    with open(TEST_ASSET_FILE) as fin:
        asset_3 = load_asset_from_file(fin)

    assert asset_1 == asset_2, (
        f"Asset {str(asset_1)} must be equal to {str(asset_2)}"
    )
    assert asset_1 == asset_3, (
        f"Asset {str(asset_1)} must be equal to {str(asset_3)}"
    )

def test_setup_parser():
    '''Test setup parser'''

    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )
    setup_parser(parser)

    assert isinstance(parser, ArgumentParser), (
        f"Parser must be type of {type(ArgumentParser)}"
    )

@mock.patch("task_Ashabokov_Aslan_asset_web_service.print")
def test_print_asset_revenue(mock_print):
    '''Test print_asset_revenue'''
    mock_print.return_value = None
    with open(TEST_ASSET_FILE) as fin:
        print_asset_revenue(fin, list(range(1, 10)))
