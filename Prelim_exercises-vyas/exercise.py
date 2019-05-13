#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
import os
from mynames import *


def open_file(path):
    """Open and return the file specified by path."""
    if os.path.exists(path):
        return open(path)
    else:
        print("Error! file path doesn't exist.")
        sys.exit()

def get_next_character(input_file):
    """Read and return the next character in input_file."""
    next_char = input_file.read(1)
    if next_char == None:
        next_char = ""
    return next_char



def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    next_char = get_next_character(input_file)
    while next_char.isspace():
        next_char = get_next_character(input_file)
    return next_char

def get_next_number(input_file):
    """Seek the next number in input_file.
    Return the number (or None) and the next non-numeric character.
    """
    num = 1
    next_char = get_next_character(input_file)
    while not next_char.isdigit():
        next_char = get_next_character(input_file)
        if next_char == "":
            num = None
            break;

    next_non_digit = ""
    if num != None:
        num_str = next_char
        while next_char.isdigit():
            next_char = get_next_character(input_file)
            num_str = num_str + next_char
        next_non_digit = num_str[-1]
        num = int(num_str[:-1])
    return [num,next_non_digit]


def get_next_name(input_file):
    """Seek the next name string in input_file.
    Return the name string (or None) and the next non-alphanumeric character.
    """
    name = ""
    next_char = get_next_character(input_file)
    while not next_char.isalpha():
        next_char = get_next_character(input_file)
        if next_char == "":
            name = None
            break;
    next_non_alnum = ""
    if name != None:
        str = next_char
        while next_char.isalnum():
            next_char = get_next_character(input_file)
            str = str + next_char
        next_non_alnum = str[-1]
        name = str[:-1]
    return [name, next_non_alnum]

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
        path = arguments[0]
        print(path)
        file = open_file(path)

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        char = get_next_character(file)
        while(char != ""):
            print(char, end = '')
            char = get_next_character(file)

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        position = file.seek(0,0)
        char = get_next_non_whitespace_character(file)
        while(char != ""):
            print(char, end = '')
            char = get_next_non_whitespace_character(file)

        print("\nNow reading numbers...")
        # Print out all the numbers in the file
        position = file.seek(0,0)
        num_char = get_next_number(file)
        while (num_char[1] !="" and num_char[0] != None):
            print(num_char[0], end = " ")
            num_char = get_next_number(file)

        print("\nNow reading names...")
        # Print out all the names in the file
        position = file.seek(0,0)
        name_char = get_next_name(file)
        while (name_char[1] !="" and name_char[0] != None):
            print(name_char[0], end = " ")
            name_char = get_next_name(file)

        print("\nNow censoring bad names...")
        # Print out only the good names in the file
        position = file.seek(0,0)
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                         name.lookup("Ghastly"), name.lookup("Awful")]

        name_char = get_next_name(file)
        bad_names = [name.get_string(id) for id in bad_name_ids]
        while (name_char[1] !="" and name_char[0] != None):

            if not(name_char[0] in bad_names):
                print(name_char[0], end = " ")
            name_char = get_next_name(file)




if __name__ == "__main__":
    main()
