#!/usr/bin/env python
'''
WebSpy module

Loads HTML and compares with HTML local dump
'''

import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

import requests
from bs4 import BeautifulSoup


FREE_SEARCH_FILTER = {"title": "Available in GitLab SaaS Free"}
NONFREE_SEARCH_FILTER = {"title": "Not available in SaaS Free"}


URL = 'https://about.gitlab.com/features/'
BS_PARSER = 'html.parser'


def get_html(url: str) -> str:
    '''Loads html from WEB'''
    response = requests.get(url)
    return response.text

def parse_html(url: str) -> tuple:
    '''Parse HTML and get free and non free elements count'''
    row_html = get_html(url)
    soup = BeautifulSoup(row_html, BS_PARSER)
    free_count = len(soup.find_all("a", FREE_SEARCH_FILTER))
    non_free_count = len(soup.find_all("a", NONFREE_SEARCH_FILTER))

    return free_count, non_free_count


def gitlab_parser_callback(args: Namespace):
    '''Parse GitLab website'''
    free_count, non_free_count = parse_html(args.url)
    print(f"free products: {free_count}", file=sys.stdout)
    print(f"enterprise products: {non_free_count}", file=sys.stdout)

def setup_parser():
    '''Setup parser'''
    parser = ArgumentParser(
        prog='WebSpy',
        description='GitLab web spy',
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=True,
        argument_default='-h',
    )
    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        required=True,
        description='WebSpy',
    )
    subparsers.required = True
    gitlab_parser = subparsers.add_parser(
        'gitlab',
        help='Get free features list from GitLab website',
        description='WebSpy subparser for GitLab',
    )
    gitlab_parser.add_argument(
        '-u',
        '--url',
        help='Target URL',
        required=False,
        default=URL,
    )
    gitlab_parser.set_defaults(callback=gitlab_parser_callback)

    return parser

def main():
    '''Main function for calling as script'''
    parser = setup_parser()
    args = parser.parse_args()
    args.callback(args)


if __name__ == '__main__':
    main()
