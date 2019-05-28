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
    "Create a names instance."
    return Names()

@pytest.fixture
def trial_devices():
    "Create a devices instance"
    return devices(names_mod)

@pytest.fixture
def trial_network():
    "Create network instance"
    return network(trial_names, trial_devices)

@pytest.fixture
def trial_monitors():
    "Creates monitors instance"
    return monitors(trial_names, trial_devices, trial_network)

@pytest.fixture
def trial_scanner1():
    "Create scanner for first file."
    path1  = "parse_test_files/test_1.txt"
    return scanner(path1, trial_names)

def test_parse_network():
    "Feed a file known to be incorrect."
    test_parse = Parser(trial_names, trial_devices, trial_network,
                        trial_monitors, trial_scanner1)
    assert test_parse.parse_network == False
