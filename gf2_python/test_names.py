"""Test the names module."""

import pytest
from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get_name_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_name_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_name_string(name_id) is None


def test_query_raises_exceptions(used_names):
    """Test if query raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.query(5)


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve")
])
def test_query(used_names, new_names, name_id, expected_string):
    """Test if look_up returns the expected name_id"""
    # id is present
    assert used_names.query(expected_string) == name_id
    # id is absent
    assert new_names.query(expected_string) is None


def test_lookup_raises_exceptions(used_names):
    """Test if query raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.lookup("hey")
    with pytest.raises(TypeError):
        used_names.lookup(["Yo James", "hi Vyas", 3])


@pytest.mark.parametrize("name_ids, expected_string_list", [
    ([0], ["Alice"]),
    ([1, 2], ["Bob", "Eve"]),
    ([2, 0], ["Eve", "Alice"]),
])
def test_lookup(used_names, new_names, name_ids, expected_string_list):
    """Test if look_up returns the expected name_ids"""
    # all ids present
    assert used_names.lookup(expected_string_list) == name_ids
    # all ids absent
    assert len(new_names.lookup(expected_string_list))\
        == len(expected_string_list)


def test_unique_error_codes(new_names):
    """Test that unique_error_codes returns unique codes"""
    codes = new_names.unique_error_codes(10)
    numbers = []
    for i in codes:
        numbers.append(i)
    assert numbers == list(set(numbers))


def test_unique_error_codes_raises_exceptions(new_names):
    """Test that unique_error_codes raises expected exceptions"""
    with pytest.raises(TypeError):
        new_names.unique_error_codes('Hello')
    with pytest.raises(TypeError):
        new_names.unique_error_codes(1.5)
    with pytest.raises(ValueError):
        new_names.unique_error_codes(-1)
