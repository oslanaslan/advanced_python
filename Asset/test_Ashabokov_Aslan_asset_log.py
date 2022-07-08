"""
Tests for asset module
"""

from argparse import ArgumentParser, Namespace
import logging

from asset import Asset, load_asset_from_file, process_cli_arguments, \
    setup_logging, setup_parser


ASSET_PATH = 'asset.txt'
DEBUG_LOG_PATH = "asset_log.debug"
WARN_LOG_PATH = "asset_log.warn"
LOGGING_CONF_PATH = 'task_Ashabokov_Aslan_asset_log.conf.yml'
RAW_ASSET = 'property   1000    0.1'
APP_NAME = 'asset'
CMD_ARGS = [
    '--logging-config',
    'task_*asset_log.conf.yml',
    '--filepath',
    'asset.txt',
    '--periods',
    '1',
    '2',
    '5'
]

# Base tests

def test_setup_parser():
    """Test logging setup from cfg file"""
    parser = ArgumentParser(
        prog="asset",
        description="tool to forecast asset revenue",
    )

    setup_parser(parser)

    assert parser.description == "tool to forecast asset revenue"
    assert parser.prog == "asset"

def test_assert_magic_functions(tmp_path):
    """Test asset magic functions"""
    true_asset = Asset(
        name='property',
        capital=1000.0,
        interest=0.1,
    )

    false_asset = Asset(
        name='property',
        capital=100,
        interest=0.1,
    )

    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)

    with open(path, 'r') as fin:
        asset = load_asset_from_file(fin)

    assert true_asset == asset, (
        f"True asset: {true_asset}\nGot: {asset}\n"
    )
    assert false_asset != asset, (
        f"False asset: {false_asset}\nGot: {asset}\n"
    )
    assert str(true_asset) == str(asset), (
        f"True asset repr: {true_asset.__repr__()}\nGot: {asset.__repr__()}\n"
    )

def test_build_asset_from_string():
    """Test build asset from string"""
    asset = Asset.build_from_str(RAW_ASSET)
    true_asset = Asset(
        name='property',
        capital=1000.0,
        interest=0.1,
    )

    assert true_asset == asset, (
        f"True asset: {true_asset}\nGot: {asset}\n"
    )

def test_build_asset_from_file(tmp_path):
    """Test build asset from file"""
    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)
    with open(path, 'r') as fin:
        asset = load_asset_from_file(fin)
    true_asset = Asset(
        name='property',
        capital=1000.0,
        interest=0.1,
    )

    assert true_asset == asset, (
        f"True asset: {true_asset}\nGot: {asset}\n"
    )


def test_load_asset_from_file(tmp_path):
    """Test load asset from file"""
    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)
    with open(path, 'r') as fin:
        asset = load_asset_from_file(fin)

    true_asset = Asset(
        name='property',
        capital=1000.0,
        interest=0.1,
    )

    assert true_asset == asset

def test_setup_logging():
    """Test setup parser"""
    setup_logging(LOGGING_CONF_PATH)
    logger = logging.getLogger(APP_NAME)

    assert len(logger.handlers) == 3, (
        f"logger must have 3 handlers\nGot: {logger.handlers}"
    )

def test_process_cli_arguments(capsys, tmp_path):
    """Test main function"""
    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)
    arguments = Namespace(
        asset_fin=open(path, 'r'),
        periods=[1, 2, 5],
    )
    true_result = '1:100.0002:210.0005:610.510'
    process_cli_arguments(arguments)
    captured = capsys.readouterr().out
    captured = captured.strip().split()
    captured = ''.join([i.strip() for i in captured])
    assert true_result == captured

# Logging tests

def test_logging_debug_and_warn(tmp_path):
    """Test logging"""
    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)
    arguments = Namespace(
        asset_fin=open(path, 'r'),
        periods=[1, 2, 5, 7, 10, 11],
        logging_yaml_config_fpath=LOGGING_CONF_PATH,
    )

    setup_logging(LOGGING_CONF_PATH)
    process_cli_arguments(arguments)

    with open(DEBUG_LOG_PATH, 'r') as fin:
        logs = fin.readlines()
        assert any('DEBUG' in log for log in logs), (
            "DEBUG not in debug file"
        )
        assert any('INFO' in log for log in logs), (
            "INFO not in debug file"
        )
        assert any('WARNING' in log for log in logs), (
            "WARNING not in debug file"
        )

    with open(WARN_LOG_PATH, 'r') as fin:
        logs = fin.readlines()
        assert not any('DEBUG' in log for log in logs), (
            "DEBUG in warn file"
        )
        assert not any('INFO' in log for log in logs), (
            "INFO in warn file"
        )
        assert any('WARNING' in log for log in logs), (
            "WARNING not in debug file"
        )

# Logging output tests

def test_logging_stderr(capsys, tmp_path):
    """Test logging to stderr"""
    path = tmp_path / ASSET_PATH
    with open(path, 'w') as fout:
        fout.write(RAW_ASSET)
    arguments = Namespace(
        asset_fin=open(path, 'r'),
        periods=[1, 2, 5, 7, 10, 11],
        logging_yaml_config_fpath=LOGGING_CONF_PATH,
    )

    setup_logging(LOGGING_CONF_PATH)
    process_cli_arguments(arguments)

    captured = capsys.readouterr().err

    assert "DEBUG" not in captured, (
        "DEBUG in stderr"
    )
    assert "INFO" in captured, (
        "INFO not in stderr"
    )
    assert "WARNING" in captured, (
        "WARNING not in stderr"
    )
