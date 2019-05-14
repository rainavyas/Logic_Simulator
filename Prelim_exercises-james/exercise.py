#!/usr/bin/env python3
"""Preliminary exercises for Part IIA Project GF2."""
import sys
import os
from mynames import MyNames


def open_file(path):
    """Open and return the file specified by path."""
    try:
        file = open(path, 'r')
    except IOError:
        print("Invalid file path.")
        sys.exit()
    else:
        return file


def get_next_character(input_file):
    """Read and return the next character in input_file."""
    return input_file.read(1)


def get_next_non_whitespace_character(input_file):
    """Seek and return the next non-whitespace character in input_file."""
    char = input_file.read(1)
    if char.isspace():
        out = ''
    else:
        out = char
    return out


def get_next_number(input_file):
    """Seek the next number in input_file.

    Return the number (or None) and the next non-numeric character.
    """
    num = []
    lis = []

    char = input_file.read(1)

    if char.isdigit():
        while char.isdigit():
            num.append(char)
            char = input_file.read(1)
        num = ''.join(map(str, num))
        lis.append(num)
        lis.append(char)
        return lis
    else:
        return


def get_next_name(input_file):
    """Seek the next name string in input_file.

    Return the name string (or None) and the next non-alphanumeric character.
    """
    name = []
    lis = []

    char = input_file.read(1)

    if char.isalpha():
        while char.isalnum():
            name.append(char)
            char = input_file.read(1)
        name = ''.join(map(str, name))
        lis.append(name)
        lis.append(char)
        return lis
    else:
        return


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
        path = os.getcwd() + "/example.txt"
        print("File path is:", path)
        print("\nFile contents are:")
        print(open_file(path).read())

        print("\nNow reading file...")
        # Print out all the characters in the file, until the end of file
        with open_file(path) as file:
            while file.tell() < len(open_file(path).read()):
                c = get_next_character(file)
                print(c, end="")

        print("\nNow skipping spaces...")
        # Print out all the characters in the file, without spaces
        with open_file(path) as file:
            while file.tell() < len(open_file(path).read()):
                d = get_next_non_whitespace_character(file)
                print(d, end="")
            print(' ')

        print("\n\nNow reading numbers...")
        # Print out all the numbers in the file
        with open_file(path) as file:
            while file.tell() < len(open_file(path).read()):
                e = get_next_number(file)
                print(e)
            print(' ')

        print("\nNow reading names...")
        # Print out all the names in the file

        with open_file(path) as file:
            while file.tell() < len(open_file(path).read()):
                f = get_next_name(file)
                print(f)
            print(' ')

        print("\nNow censoring bad names...")
        # Print out the ID for each bad name.
        name = MyNames()
        bad_name_ids = [name.lookup("Terrible"), name.lookup("Horrid"),
                        name.lookup("Ghastly"), name.lookup("Awful")]
        print("Bad IDs are:", bad_name_ids)

        with open_file(path) as file:
            while file.tell() < len(open_file(path).read()):
                g = get_next_name(file)
                if g is not None:
                    name.lookup(g[0])

        print("\nGood names are:")
        # Print only the good names from the file.

        for n in range(len(name.name_list)):
            if n in bad_name_ids:
                pass
            else:
                print(name.get_string(n))

if __name__ == "__main__":
    main()
