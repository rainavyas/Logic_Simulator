"""Test the 'parse' module"""
import pytest

from parse import Parser
from scanner import Symbol
from names import Names
from scanner import Scanner
from monitors import Monitors
from devices import Devices
from network import Network
import sys


@pytest.fixture
def names():
    """Creates a Names instance"""
    return Names()


@pytest.fixture
def devices(names):
    """Creates a Devices instance"""
    return Devices(names)


@pytest.fixture
def network(names, devices):
    """Creates Network instance"""
    return Network(names, devices)


@pytest.fixture
def monitors(names, devices, network):
    """Creates Monitors instance"""
    return Monitors(names, devices, network)


@pytest.fixture
def file_list():
    file_list = [
                 # Correct definition file.
                 "Example.txt",
                 # Syntax error files:
                 "Error1.txt", "Error2.txt", "Error3.txt", "Error4.txt",
                 "Error5.txt", "Error6.txt", "Error7.txt","Error8.txt",
                 "Error9.txt", "Error10.txt", "Error11.txt","Error12.txt",
                 "Error13.txt", "Error14.txt", "Error15.txt","Error16.txt",
                 "Error17.txt", "Error18.txt", "Error19.txt","Error20.txt",
                 "Error21.txt", "Error22.txt", "Error23.txt",
                 # Semantic error files (devices):
                 "Error24.txt", "Error25.txt", "Error26.txt", "Error27.txt",
                 "Error28.txt",
                 # Semantic error files (connections):
                 "Error29.txt", "Error30.txt", "Error31.txt",
                 "Error32.txt", "Error33.txt",
                 # Semantic error files (monitors):
                 "Error34.txt", "Error35.txt",
                 # Correct definition file with extended monitoring points:
                 "Test_File.txt"
                 ]
    return file_list


def test_parse_network(names, devices, network, monitors, file_list):
    """Asserts whether files expected to parse or not do so"""
    #  Assert whether parsing each file returns true/false.
    for n in range(len(file_list)):
        path = "parse_test_files/" + file_list[n]
        scanner = Scanner(path, names)
        parse = Parser(names, devices, network, monitors, scanner)
        if n == 0:
            assert parse.parse_network() == True
        else:
            assert parse.parse_network() == False

@pytest.mark.parametrize("file,error_line,expected_msg", [
    # Syntax errors:
    (1, "Line 33:", "'END' keyword required at end of file"),
    (2, "Line 1:", "Expected '{' after 'DEVICES'"),
    (3, "Line 1:", "'DEVICES' keyword required"),
    (4, "Line 15:", "Expected '{' after 'CONNECT'"),
    (5, "Line 15:", "'CONNECT' keyword required"),
    (6, "Line 29:", "Expected '{' after 'MONITOR'"),
    (7, "Line 29:", "'MONITOR' keyword required"),
    (8, "Line 4:", "Needs to be a positive integer"),
    (9, "Line 5:", "Expected a parameter: 'initial', 'inputs' or 'period'"),
    (10, "Line 6:", "Expected a parameter: 'initial', 'inputs' or 'period'"),
    (11, "Line 5:", "Device definition needs to end in ';'"),
    (12, "Line 4:", "Device name has to be followed by ':'"),
    (13, "Line 6:", "Valid Device name required"),
    (14, "Line 7:", "Valid Logic gate required e.g. 'AND'"),
    (15, "Line 23:", "Output pin has to be 'Q' or 'QBAR'"),
    (16, "Line 22:", "Connection has to be terminated by ';'"),
    (17, "Line 24:", "Valid input pin required"),
    (18, "Line 25:", "'.' required to specify input pin"),
    (19, "Line 20:", "Name string of input device required"),
    (20, "Line 26:", "'=' Assignment operator requried"),
    (21, "Line 30:", "Valid string name required"),
    (22, "Line 30:", "Monitor point has to be terminated by ';'"),
    (23, "Line 11:", "Missing '}'"),
    # Semantic errors (devices):
    (24, "Line 5:", "Device Name already used"),
    (25, "Line 4:", "Expected a parameter: 'initial', 'inputs' or 'period'"),
    (26, "Line 7:", "Expected a parameter: 'initial', 'inputs' or 'period'"),
    (27, "Line 4:", "Needs to be a positive integer"),
    (28, "Line 8:", "Valid device qualifier requried"),
    # Semantic errors (connections):
    (29, "Line 12:", "Device is not declared"),
    (30, "Line 20:", "Input is already in a connection"),
    (31, "Line 23:", "Output pin has to be 'Q' or 'QBAR'"),
    (32, "Line 24:", "Valid input pin required"),
    (33, "Line 23:", "'.' required to specify input pin"),
    # Semantic errors (monitors):
    (34, "Line 31:", "Output pin has to be 'Q' or 'QBAR'"),
    (35, "Line 32:", "This point is already being monitored")
])


def test_error(names, devices, network, monitors, file_list, file, error_line,
               expected_msg):
    """Ensures all errors are correctly reported and stored for use by GUI"""

    # Create scanner and parse objects for given file.
    path = "parse_test_files/" + file_list[file]
    scanner = Scanner(path, names)
    parse = Parser(names, devices, network, monitors, scanner)
    # Parse the given file.
    parsed = parse.parse_network()
    # Initially expect the returned message to be incorrect.
    correct_message = False

    # If the line number and message are correct, set correct_message 'True'.
    for error_object in parse.scanner.error_list:
        error_msg = error_object.msg
        print("Found msg", error_msg)
        print("Expected msg", expected_msg)
        error_line_num = error_object.line_num
        print("Found line", error_line_num)
        print("Expected line", error_line)
        if error_line_num == error_line:
            if error_msg == expected_msg:
                correct_message = True

    # Assert that the line and message were returned correctly.
    assert correct_message == True
    # Close the current file to prevent a large number of open files.
    scanner.close_file()


@pytest.mark.parametrize("device_number,device_name,device_type,device_inputs,"
                         "connected_to", [
    # Known devices with their device types, inputs and expected connections.
    (0, "clock1", "CLOCK", [], []),
    (1, "clock2", "CLOCK", [], []),
    (2, "clock3", "CLOCK", [], []),
    (3, "switch1", "SWITCH", [], []),
    (4, "switch2", "SWITCH", [], []),
    (5, "nand", "NAND", ["I1", "I2"], ["dtype.Q", "switch2"]),
    (6, "xor", "XOR", ["I1", "I2"], ["nand", "switch2"]),
    (7, "dtype", "DTYPE", ["SET","DATA","CLK","CLEAR"], ["clock1", "clock2",
                                                         "clock3", "switch1"])
])

def test_devices_and_connections(names, devices, network, monitors, file_list,
                                 device_number, device_name, device_type,
                                 device_inputs, connected_to):
    """Tests whether devices have been created and have expected properties.
    Asserts that connections between devices are as expected.
    """
    # Create scanner and parse objects for given file:
    path = "parse_test_files/" + file_list[36]
    scanner  = Scanner(path, names)
    parse  = Parser(names, devices, network, monitors, scanner)
    # Parse the given file:
    parse.parse_network()
    # Assert correct number of devices created:
    assert len(devices.devices_list) == 8
    # Create device object for the current device in the list:
    device = devices.devices_list[device_number]
    # Assert that the device id and kind are consistent:
    assert names.query(device_name) == device.device_id
    assert names.query(device_type) == device.device_kind
    n = 0
    # Depending on the device, assert connections are correct:
    for input in device_inputs:
        if connected_to[n].endswith("Q"):
            assert (device.inputs.get(names.query(input))[0]
                    == names.query(connected_to[n][:-2]))
        elif connected_to[n].endswith("QBAR"):
            assert (device.inputs.get(names.query(input))[0]
                    == names.query(connected_to[n][:-5]))
        else:
            assert (device.inputs.get(names.query(input))[0]
                    == names.query(connected_to[n]))
        n += 1


@pytest.mark.parametrize("monitor_num,monitor_name", [
    # Syntax errors:
    (0, "clock1"),
    (1, "clock3"),
    (2, "switch1"),
    (3, "xor"),
    (4, "dtype.QBAR"),
    (5, "dtype.Q")
])

def test_monitors(names, devices, network, monitors, file_list, monitor_num,
                  monitor_name):
    """Tests whether monitoring points have been created correctly."""
    # Create scanner and parse objects for given file:
    path = "parse_test_files/" + file_list[36]
    scanner  = Scanner(path, names)
    parse  = Parser(names, devices, network, monitors, scanner)
    # Parse the given file:
    parse.parse_network()
    # Assert correct monitoring points created:
    if monitor_name.endswith("Q"):
        assert (list(monitors.monitors_dictionary.items())[monitor_num][0][1]
                == devices.dtype_output_ids[0])
    elif monitor_name.endswith("QBAR"):
        assert (list(monitors.monitors_dictionary.items())[monitor_num][0][1]
                == devices.dtype_output_ids[1])
    else:
        assert (list(monitors.monitors_dictionary.items())[monitor_num][0][0]
                == names.query(monitor_name))
