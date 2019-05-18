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
