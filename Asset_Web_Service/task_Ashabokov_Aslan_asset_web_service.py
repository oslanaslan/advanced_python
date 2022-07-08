#!/usr/bin/env python3
'''
Asset Web Service
'''
from argparse import ArgumentParser, FileType
import sys
import logging
import logging.config
from typing import Dict
import json
from collections import defaultdict

import requests
import yaml
from flask import Flask, jsonify, make_response, request
from bs4 import BeautifulSoup

app = Flask(__name__)
app.bank = []
app.asset_names = []

CBR_DAILY_URL = "https://www.cbr.ru/eng/currency_base/daily/"
CBR_KEY_INDICATORS_URL = "https://www.cbr.ru/eng/key-indicators/"

API_CBR_KEY_INDICATORS = "/cbr/key_indicators"
API_CBR_DAILY = "/cbr/daily"
API_CREATE_ASSET = "/api/asset/add/<char_code>/<name>/<capital>/<interest>"
API_ASSET_LIST = "/api/asset/list"
API_GET_ASSET = "/api/asset/get"
API_CALCULATE_REVENUE = "/api/asset/calculate_revenue"
API_CLEANUP = "/api/asset/cleanup"

REPORT_TAGS = ['RUB', 'USD', 'EUR', 'Au', 'Ag', 'Pt', 'Pd']
API_503_MESSAGE = "CBR service is unavailable"
API_404_MESSAGE = "This route is not found"

WARN_PERIOD_THRESHOLD = 5
logger = logging.getLogger("asset")


class Asset:
    '''
    Asset class
    '''
    def __init__(self, name: str, capital: float, interest: float):
        '''Create asset'''
        self.name = name
        self.capital = capital
        self.interest = interest

    def calculate_revenue(self, years: int) -> float:
        '''Calculate revenue'''
        revenue = self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue

    @classmethod
    def build_from_str(cls, raw: str):
        '''Create asset from string'''
        logger.debug("building asset object...")
        name, capital, interest = raw.strip().split()
        capital = float(capital)
        interest = float(interest)
        asset = cls(name=name, capital=capital, interest=interest)
        return asset

    def __repr__(self):
        '''Magic repr'''
        repr_ = f"{self.__class__.__name__}({self.name}, {self.capital}, {self.interest})"
        return repr_

    def __eq__(self, rhs):
        '''Magic eq'''
        outcome = (
            self.name == rhs.name
            and self.capital == rhs.capital
            and self.interest == rhs.interest
        )
        return outcome

class Profile:
    '''
    Composite class with assets of different type
    '''

    def __init__(self, name: str, char_code: str, capital: float, interest: float) -> None:
        '''Create profile'''
        self.asset = Asset(
            name=name,
            capital=capital,
            interest=interest,
        )
        self.char_code = char_code

    def get_asset(self) -> str:
        '''Magic repr'''
        return [
            self.char_code,
            self.asset.name,
            self.asset.capital,
            self.asset.interest,
        ]

    def __repr__(self) -> str:
        '''Magic repr'''
        return self.asset.__repr__() + f' char_code: {self.char_code}'

# Parsers

def convert_to_float(text: str) -> float:
    '''Convert string to float'''
    if ' ' in text:
        text = ''.join(text.split(' '))
    if ',' in text:
        text = ''.join(text.split(','))
    res = float(text)

    return res

def parse_cbr_currency_base_daily(html_data: str) -> Dict[str,float]:
    '''
    Parse CBR daily currency base html

    - content example: https://www.cbr.ru/eng/currency_base/daily/
    - dump example: github../cbr_currency_base_daily.html
    '''
    char_codes = {}
    parser = BeautifulSoup(html_data, "html.parser")
    tags = parser.findAll("tr")[1:]

    for tag in tags:
        subtags = tag.findAll("td")
        name = subtags[1].string
        unit = float(subtags[2].string)
        rate = float(subtags[-1].string)
        char_codes[name] = rate / unit

    return char_codes

def parse_cbr_key_indicators(html_data: str) -> Dict[str,float]:
    '''
    Parse CBR indicators html

    - content example: https://www.cbr.ru/eng/key-indicators/
    - dump example: github../cbr_key_indicators.html
    '''
    char_codes = {}
    parser = BeautifulSoup(html_data, "html.parser")
    tags = parser.findAll('div', {'class': 'key-indicator_table_wrapper'})
    currency_tags = tags[1].findAll('tr')[1:]
    active_tags = tags[2].findAll('tr')[1:]

    for tag in currency_tags:
        subtags = tag.findAll('td')
        code = subtags[0].findAll('div', {'class': 'col-md-3 offset-md-1 _subinfo'})
        code = code[0].text
        value = subtags[2].text
        char_codes[code] = convert_to_float(value)

    for tag in active_tags:
        tag_lst = tag.text.strip('\n').split('\n')
        tag_lst = [i for i in tag_lst if len(i) > 0]
        code = tag_lst[1]
        value = tag_lst[-1]
        char_codes[code] = convert_to_float(value)

    return char_codes

# API

def error_503_handler():
    '''Connection Error Handler'''
    response = make_response(API_503_MESSAGE, 503)
    response.mimetype = "text/plain"

    return response

@app.errorhandler(404)
def not_found_callback(error):
    '''Page not found 404 callback'''
    logger.error(str(error))
    response = make_response(API_404_MESSAGE, 404)
    response.mimetype = "text/plain"

    return response

@app.route(API_CBR_DAILY)
def cbr_daily_callback():
    '''Get daily CBR rates'''
    try:
        get_response = requests.get(CBR_DAILY_URL)
    except requests.exceptions.ConnectionError:
        return error_503_handler()

    char_dict = parse_cbr_currency_base_daily(get_response.text)

    return jsonify(char_dict)

@app.route(API_CBR_KEY_INDICATORS)
def cbr_indicators_callback():
    '''Get indicators from CBR website'''
    try:
        get_response = requests.get(CBR_KEY_INDICATORS_URL)
    except requests.exceptions.ConnectionError:
        return error_503_handler()

    char_dict = parse_cbr_key_indicators(get_response.text)

    return jsonify(char_dict)

@app.route(API_CREATE_ASSET)
def create_asset_callback(char_code: str, name: str, capital: str, interest: str):
    '''
    Create asset request

    Params:

    - char_code: str
    - name: str
    - capital: str
    - interest: str

    Return
    - response: flask.Response
    '''

    capital = float(capital)
    interest = float(interest)

    profile = Profile(
        name=name,
        char_code=char_code,
        capital=capital,
        interest=interest,
    )

    if name in app.asset_names:
        response = make_response(
            f"Asset {name} already exists",
            403,
        )
        response.mimetype = "text/plane"
    else:
        app.bank.append(profile)
        app.asset_names.append(name)
        response = make_response(
            f"Asset {name} was successfully added",
            200,
        )
        response.mimetype = "text/plane"

    return response

@app.route(API_ASSET_LIST)
def get_asset_list_callback():
    '''Get all saved assets'''
    all_assets = []
    for asset in app.bank:
        all_assets.append(asset.get_asset())

    all_assets = sorted(all_assets)
    response = jsonify(all_assets)

    return response

@app.route(API_GET_ASSET)
def get_asset_callback():
    '''Get asset by parameters'''
    query = request.args.getlist('name')
    all_assets = []

    for asset in app.bank:
        if asset.asset.name in query:
            all_assets.append(asset.get_asset())

    all_assets = sorted(all_assets)
    response = jsonify(all_assets)

    return response

@app.route(API_CALCULATE_REVENUE)
def calculate_revenue_callback():
    '''Calculate revenue with given periods'''
    query = request.args.getlist('period')
    cbr_daily_rates = cbr_daily_callback().get_data()
    cbr_daily_rates = json.loads(cbr_daily_rates)
    cbr_indicators = cbr_indicators_callback().get_data()
    cbr_indicators = json.loads(cbr_indicators)
    all_revenue = defaultdict(lambda: 0)

    for period in query:
        current_revenue = 0

        for profile in app.bank:
            current_char_code = profile.char_code
            current_asset = profile.asset

            if current_char_code != "RUB":
                if current_char_code in cbr_indicators:
                    current_capital = current_asset.capital * \
                        cbr_indicators[current_char_code]
                else:
                    current_capital = current_asset.capital * \
                        cbr_daily_rates[current_char_code]

                current_asset = Asset(
                    name=current_asset.name,
                    capital=current_capital,
                    interest=current_asset.interest,
                )

            current_revenue += current_asset.calculate_revenue(float(period))

        all_revenue[period] += current_revenue

    response = jsonify(all_revenue)

    return response

@app.route(API_CLEANUP)
def cleanup_callback():
    '''Delete all assets'''
    app.bank = []
    app.asset_names = []
    msg = "there are no more assets"
    response = make_response(msg, 200)

    return response

# Functions

def load_asset_from_file(fileio):
    '''Load asset from file'''
    logger.info("reading asset file...")
    raw = fileio.read()
    asset = Asset.build_from_str(raw)
    return asset


def process_cli_arguments(arguments):
    '''Process args'''
    print_asset_revenue(arguments.asset_fin, arguments.periods)


def print_asset_revenue(asset_fin, periods):
    '''Print asset revenue'''
    asset = load_asset_from_file(asset_fin)

    if len(periods) >= WARN_PERIOD_THRESHOLD:
        logger.warning("too many periods were provided: %s", len(periods))

    for period in periods:
        revenue = asset.calculate_revenue(period)
        logger.debug("asset %s for period %s gives %s", asset, period, revenue)
        print(f"{period:5}: {revenue:10.3f}")


def setup_logging(logging_yaml_config_fpath):
    """setup logging via YAML if it is provided"""
    if logging_yaml_config_fpath:
        with open(logging_yaml_config_fpath) as config_fin:
            logging.config.dictConfig(yaml.safe_load(config_fin))


def setup_parser(parser):
    '''Setup parser'''
    parser.add_argument("-f", "--filepath", dest="asset_fin", default=sys.stdin, type=FileType("r"))
    parser.add_argument("-p", "--periods", nargs="+", type=int, metavar="YEARS", required=True)
    parser.add_argument(
        "--logging-config", dest="logging_yaml_config_fpath",
        default=None, help="path to logging config in YAML format",
    )
    parser.set_defaults(callback=process_cli_arguments)


def main():
    '''Main script function'''
    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    setup_logging(arguments.logging_yaml_config_fpath)
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
