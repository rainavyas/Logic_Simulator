"""Test the scanner module"""

import pytest
from names import Names
from scanner import Scanner


@pytest.fixture
def file_path_list():
    """Return a list of different file paths"""
    path0 = "scanner_test_files/test0.txt"
    path1 = "scanner_test_files/test1.txt"
    path2 = "scanner_test_files/test2.txt"
    path3 = "scanner_test_files/test3.txt"
    path4 = "scanner_test_files/test4.txt"
    path5 = "scanner_test_files/test5.txt"
    return [path0, path1, path2, path3, path4, path5]


def test_get_name(file_path_list):
    """Test if get_name returns the name"""
    path = file_path_list[0]
    test_scanner = Scanner(path, Names())
    name = test_scanner.get_name()
    assert name == "testString"


def test_get_number(file_path_list):
    """Test if get_number returns the number"""
    path = file_path_list[1]
    test_scanner = Scanner(path, Names())
    num = test_scanner.get_number()
    assert num == "1234567"


def test_advance(file_path_list):
    """Test the advance function progresses by one character"""
    path = file_path_list[0]
    test_scanner = Scanner(path, Names())
    test_scanner.advance()
    assert test_scanner.current_character == "e"


def test_skip_spaces(file_path_list):
    """Test the skip_spaces skips whitespace"""
    path = file_path_list[2]
    test_scanner = Scanner(path, Names())
    test_scanner.skip_spaces()
    assert test_scanner.current_character == "S"


def test_skip_comment_single(file_path_list):
    """Test single line comments are skipped"""
    path = file_path_list[3]
    test_scanner = Scanner(path, Names())
    test_scanner.skip_comment()
    assert test_scanner.current_character == "X"


def test_skip_comment_multi(file_path_list):
    """Test mutli line comments are skipped"""
    path = file_path_list[4]
    test_scanner = Scanner(path, Names())
    test_scanner.skip_comment()
    assert test_scanner.current_character == "X"


def test_location(file_path_list):
    """Test the correct line and position are returned"""
    path = file_path_list[4]
    test_scanner = Scanner(path, Names())
    test_scanner.advance()
    test_scanner.advance()
    [line, pos] = test_scanner.location()
    assert line == 1
    assert pos == 3


def test_print_location_false(file_path_list):
    """Test correct line and position is returned with False option"""
    path = file_path_list[5]
    test_scanner = Scanner(path, Names())
    symb = test_scanner.get_symbol()
    symb = test_scanner.get_symbol()
    err = test_scanner.print_location(symb)
    assert err.line_num == ("Line " + str(2) + ":")


def test_print_location_true(file_path_list):
    """Test correct line and position is returned with True option"""
    path = file_path_list[5]
    test_scanner = Scanner(path, Names())
    symb = test_scanner.get_symbol()
    symb = test_scanner.get_symbol()
    err = test_scanner.print_location(symb, True)
    assert err.line_num == ("Line " + str(1)+":")


def test_get_symbol(file_path_list):
    """Test the correct symbol is returned by scanner"""
    path = file_path_list[5]
    test_scanner = Scanner(path, Names())
    symb = test_scanner.get_symbol()
    symb = test_scanner.get_symbol()
    assert symb.type == test_scanner.NUMBER
    assert symb.line == 2
