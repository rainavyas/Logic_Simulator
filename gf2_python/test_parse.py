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
    path = 'parse_test_files/test_1(incorrect).txt'
    scanner1 = Scanner(path, trial_names)
    return scanner1


@pytest.fixture
def trial_scanner2(trial_names):
    path = 'parse_test_files/test_2(correct).txt'
    scanner2 = Scanner(path, trial_names)
    return scanner2


def test_parse_network(trial_names, trial_devices, trial_network,
                       trial_monitors, trial_scanner1, trial_scanner2):
    "Feed a file known to be incorrect."

    test_parse1 = Parser(trial_names, trial_devices, trial_network,
                         trial_monitors, trial_scanner1)
    test_parse2 = Parser(trial_names, trial_devices, trial_network,
                         trial_monitors, trial_scanner2)
    assert test_parse1.parse_network() == False
    assert test_parse2.parse_network() == True
