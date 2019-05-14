#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    try:
       file = open(path)
    except IOError:
       print("Error: can\'t find file or read data")
       sys.exit()
    return file


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    char = input_file.read(1)
    return char


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    char = input_file.read(1)
    while char.isspace() is True:
        char = input_file.read(1)
    return char


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    char = input_file.read(1)
    number = ''
    while char.isdigit() is False:
        char = input_file.read(1)
        if char == '':
            return [None, '']
    while char.isdigit() is True:
        number += char
        char = input_file.read(1)
    return [int(number), char]


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    char = input_file.read(1)
    name = ''
    while char.isalpha() is False:
        char = input_file.read(1)
        if char == '':
            return [None, '']
    while char.isdigit() | char.isalpha() is True:
        name += char
        char = input_file.read(1)
    return [name, char]


def main():
    """Preliminary exercises for Part IIA Project GF2."""

    # Check command line arguments
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print("Error! One command line argument is required.")
        sys.exit()

    else:

        print("\nNow opening file...")
        # Print the path provided and try to open the file for reading
        print(arguments[0])
        file = open_file(arguments[0])

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        endReached = False
        while endReached is False:
            char = get_next_character(file)
            if char != '':
                print(char, end='')
            else:
                print(char)
                endReached = True

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        file.seek(0, 0)
        endReached = False
        while endReached is False:
            char = get_next_non_whitespace_character(file)
            if char != '':
                print(char, end='')
            else:
                print(char)
                endReached = True

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        file.seek(0, 0)
        endReached = False
        while endReached is False:
            char = get_next_number(file)
            if char != [None, '']:
                print(char, end='')
            else:
                print(char)
                endReached = True

        print("\nNow reading names...")
        # Print out all the names in the file
        file.seek(0, 0)
        name = MyNames()
        name_ids = []
        endReached = False
        while endReached is False:
            char = get_next_name(file)
            if char != [None, '']:
                name_ids.append(name.lookup(char[0]))
                print(char, end='')
            else:
                print(char)
                endReached = True

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        for i in name_ids:
            if i not in bad_name_ids:
                print(name.get_string(i))

if __name__ == "__main__":
    main()
