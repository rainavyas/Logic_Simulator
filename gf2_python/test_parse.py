import pytest
from parse import Parser
from scanner import Symbol
from names import Names
from scanner import Scanner
from monitors import Monitors
from devices import Devices
from network import Network

@pytest.fixture
def trial_names():
    return Names()

@pytest.fixture
def trial_devices(trial_names):
    """Create a devices instance"""
    return Devices(trial_names)

@pytest.fixture
def trial_network(trial_names, trial_devices):
    """Create network instance"""
    return Network(trial_names, trial_devices)

@pytest.fixture
def trial_monitors(trial_names, trial_devices, trial_network):
    """Creates monitors instance"""
    return Monitors(trial_names, trial_devices, trial_network)

@pytest.fixture
def trial_scanner1(trial_names):
    """Trial scanned file known to be incorrect"""
    path = 'parse_test_files/test_1(incorrect).txt'
    scanner1 = Scanner(path, trial_names)
    return scanner1

@pytest.fixture
def trial_scanner2(trial_names):
    """Trial scanned file known to be correct"""
    path = 'parse_test_files/test_2(correct).txt'
    scanner2 = Scanner(path, trial_names)
    return scanner2

@pytest.fixture
def parse_incorrect(trial_names, trial_devices, trial_network,
                    trial_monitors, trial_scanner1, trial_scanner2):
    """Parse a file known to be incorrect."""
    parse_incorrect = Parser(trial_names, trial_devices, trial_network,
                        trial_monitors, trial_scanner1)
    return parse_incorrect

@pytest.fixture
def parse_correct(trial_names, trial_devices, trial_network,
                    trial_monitors, trial_scanner1, trial_scanner2):
    """Parse a file known to be correct"""
    parse_correct = Parser(trial_names, trial_devices, trial_network,
                        trial_monitors, trial_scanner2)
    return parse_correct

def test_parse_type_errors(trial_names, trial_devices, trial_network,
                    trial_monitors, trial_scanner1, trial_scanner2):
    with pytest.raises(TypeError):
        Parser((1, 3, 3))

def test_parse_network(parse_incorrect, parse_correct):
    assert parse_incorrect.parse_network() == False
    assert parse_correct.parse_network() == True

# def test_error():
#
#     test_parse = Parser()  # Add variables
#
#     assert test_parse.error_count = # Add here
