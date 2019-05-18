"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from names import Names
import sys
import os

class Symbol:

    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None
        self.line = None
        self.position = None

class Scanner:

    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        self.file = open_file(path)

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
            self.KEYWORD, self.NUMBER, self.NAME, self.EOF] = range(7)
        self.keywords_list = ["DEVICES", "CONNECT", "MONITOR", "END"]
        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
            self.END_ID] = self.names.lookup(self.keywords_list)
        self.current_character = ""

    def open_file(path):
        """Open and return the file specified by path."""
        try:
            file = open(path, 'r')
        except IOError:
            print("Invalid file path.")
            sys.exit()
        else:
            return file

    def get_name():
        """Seek the next name string in input_file.

        Return the name string (or None) and place the next non-alphanumeric character in current_character.
        """
        name = []
        lis = []

        char = self.file.read(1)

        if char.isalpha():
            while char.isalnum():
                name.append(char)
                char = self.file.read(1)
            name = ''.join(map(str, name))
            self.current_character = self.file.read(1)
            return name
        else:
            return None

    def get_number():
        """Seek the next number in input_file.

        Return the number (or None) and place the next non-numeric character in current_character.
        """
        num = []

        char = self.file.read(1)

        if char.isdigit():
            while char.isdigit():
                num.append(char)
                char = self.file.read(1)
            num = ''.join(map(str, num))
            self.current_character = self.file.read(1)
            return num
        else:
            return None

    def advance():
        """Read the next character from input_file and place it in current_character.
        """
        self.current_character = self.file.read(1)

    def skip_spaces():
        """Calls advance as necessary until current_character is not whitsepace
        """
        while self.current_character.isspace():
            advance(self.file)
        else:
            return

    def location():
        """Print the current input line along with a marker showing error position in the line
        """
        current_pos = self.file.tell()

        self.file.seek(0)
        linelengths = []
        i = 0
        for line in self.file:
            i += 1
            if len(linelengths) == 0:
                linelengths.append(len(line))
            else:
                linelengths.append(len(line) + linelengths[-1])
        num_line = i

        self.line = ''
        self.position = ''
        self.file.seek(current_pos)

        for n in range(num_line):
            if n == 0:
                if self.file.tell() <= linelengths[n]:
                    self.line = 1
                    self.position = self.file.tell()
                else:
                    self.line = ''
                    self.position = ''
            elif self.file.tell() <= linelengths[n] and self.file.tell() > linelengths[n-1]:
                self.line = n + 1
                self.position = file_test.tell() - linelengths[n-1]

        marker = 0

        self.file.seek(0)

        for line in self.file:
            marker += 1
            if marker == self.line:
                print(line, " "*(self.position-3), "^")

        self.file.seek(current_pos)

    def skip_comment():
        if self.current_character == "#":
            while self.current_character != " ":
                self.advance()

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol.

        Break if 'END' reached.
        """

        symbol = Symbol()
        self.skip_spaces()  # current character now not whitespace
        self.skip_comment() # current character now not comment
        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            elif name_string = "END":
                symbol.type = self.EOF
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # number
            symbol.id = self.get_number()
            symbol.type = self.NUMBER

        elif self.current_character == "=":  # equals
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",": # comma
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ";": # semicolon
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
        else:  # not a valid character
            self.advance()
        return symbol

path_test = os.getcwd() + "/(temp)text_file.txt"
object = Scanner(path_test, names)
