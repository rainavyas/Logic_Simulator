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
        # Keep a record of the current symbol's line and position.
        self.line = None
        self.position = None
        # Keep a record of the previous symbol's line and position.
        self.prev_line = None
        self.prev_position = None


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
        #  Open the file.
        self.file = open(path)

        #  Assign names module for reference.
        self.names = names

        #  Create a list of possible types and assign them a suitable integer.
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
                                 self.KEYWORD, self.LOGIC_TYPE, self.OUT_PIN,
                                 self.IN_PIN, self.NUMBER, self.NAME,
                                 self.PERIOD, self.COLON, self.EOF,
                                 self.LEFT_CURLY, self.RIGHT_CURLY] = range(14)

        #  Create a list of keywords, logic types, input and output pins.
        self.keywords_list = ["DEVICES", "CONNECT", "MONITOR", "END",
                              "initial", "period", "inputs"]
        self.logic_type_list = ["CLOCK", "SWITCH", "AND", "NAND",
                                "OR", "NOR", "DTYPE", "XOR"]
        self.input_pin_list = ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8",
                               "I9", "I10", "I11", "I12", "I13", "I14", "I15",
                               "I16", "DATA", "CLK", "SET", "CLEAR"]
        self.output_pin_list = ["Q", "QBAR"]

        #  Assign keywords an id using the "Names" module's "lookup" function.
        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
         self.END_ID, self.initial_ID, self.period_ID,
         self.inputs_ID] = self.names.lookup(self.keywords_list)
        self.current_character = self.file.read(1)

    def get_name(self):
        """Seek the next name string in input_file.

        Return the name string (or None) and place the next non-alphanumeric
        character in current_character.
        """
        name = []
        lis = []

        if self.current_character.isalpha():
            while self.current_character.isalnum():
                name.append(self.current_character)
                self.advance()
            name = ''.join(map(str, name))
        return name

    def get_number(self):
        """Seek the next number in input_file.

        Return the number (or None) and place the next non-numeric character
        in current_character.
        """
        num = []

        #  Return a string of all consecutive numeric characters.
        while self.current_character.isdigit():
            num.append(self.current_character)
            self.advance()
        num = ''.join(map(str, num))
        return num

    def advance(self):
        """Read the next character from input_file and place it
        in current_character.
        """
        self.current_character = self.file.read(1)

    def skip_spaces(self):
        """Calls advance as necessary until current_character is not whitsepace
        """
        while self.current_character.isspace():
            self.advance()

    def skip_comment(self):
        """Skips single line comments (beginning with '#')
        and closed-comments (of form /* */)
        """
        #  Skip single-line comments.
        if self.current_character == "#":
            self.file.readline()
            self.advance()

        #  Skip closed comments.
        if self.current_character == "/":
            self.advance()
            if self.current_character == "*":
                self.advance()
                while not self.current_character == "*":
                    #  Check whether EOF reached before comment closed.
                    if self.current_character == "":
                        print("""ERROR: EOF reached. Comment not closed
                              correctly. Missing '*'.""")
                        break
                    self.advance()
                self.advance()
                #  Comment closed so advance and skip spaces.
                if self.current_character == "/":
                    self.advance()
                #  Comment not closed correctly as "/" is missing.
                elif not self.current_character == "/":
                    print("""ERROR: Comment terminated incorrectly.
                          Missing '/'.""")
                    comment_symbol = Symbol()
                    comment_symbol.line = self.location()[0]
                    comment_symbol.position = self.location()[1]
                    self.print_location(comment_symbol)
            #  Closed comment missing "*" to start.
            else:
                print("""Forward slash skipped but adjacent '*' not found
                      (closed comment not started).""")
        self.skip_spaces()

    def location(self):
        """Return the current line and position within the file.
        """

        #  Store the current position.
        stored_position = self.file.tell()

        #  Return to the file's beginning and create an empty list of lengths.
        self.file.seek(0)
        linelengths = []

        i = 0

        #  Occupy the list with cumulative line lengths.
        for line in self.file:
            i += 1
            if len(linelengths) == 0:
                linelengths.append(len(line))
            else:
                linelengths.append(len(line) + linelengths[-1])

        num_line = i

        current_line = ''
        current_position = ''

        #  Return to the stored (current) position within the file.
        self.file.seek(stored_position)

        #  Return line and position by comparing current position to the list.
        for n in range(num_line):
            if n == 0:
                if self.file.tell() <= linelengths[n]:
                    current_line = n + 1
                    current_position = self.file.tell()
            elif(self.file.tell() <= linelengths[n] and self.file.tell() >
                 linelengths[n-1]):
                current_line = n + 1
                current_position = self.file.tell() - linelengths[n-1]

        return [current_line, current_position]

    def print_location(self, symbol, option=False):
        """Print the line that the passed symbol is on and a caret on the line
         below to indicate the final character of the symbol.
        """

        #  Store the current position.
        stored_position = self.file.tell()

        #  Return to the beginning of the file.
        self.file.seek(0)

        marker = 0

        #  User wants to print the current symbol's line and position.
        if option is False:
            for line in self.file:
                marker += 1
                if marker == symbol.line:
                    print("Line " + str(symbol.line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.position-2)*" " + "^")

        #  User wants to print the last symbol's line and position.
        elif option is True:
            for line in self.file:
                marker += 1
                if marker == symbol.prev_line:
                    print("Line " + str(symbol.prev_line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.prev_position-2)*" " + "^")

        #  Return to the stored (current) position.
        self.file.seek(stored_position)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol.

        Break if 'END' reached.
        """

        #  Create symbol object and record the previous line and position.
        symbol = Symbol()
        symbol.prev_line = self.location()[0]
        symbol.prev_position = self.location()[1]

        self.skip_spaces()  # current character now not whitespace
        self.skip_comment()  # current character now not comment

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
            elif name_string in self.logic_type_list:
                symbol.type = self.LOGIC_TYPE
            elif name_string in self.output_pin_list:
                symbol.type = self.OUT_PIN
            elif name_string in self.input_pin_list:
                symbol.type = self.IN_PIN
            else:
                symbol.type = self.NAME
            [symbol.id] = self.names.lookup([name_string])

        elif self.current_character.isdigit():  # number
            [symbol.id] = self.names.lookup([self.get_number()])
            symbol.type = self.NUMBER

        elif self.current_character == "=":  # equals
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",":  # comma
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ";":  # semicolon
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ".":  # period
            symbol.type = self.PERIOD
            self.advance()

        elif self.current_character == "":  # end of file
            symbol.type = self.EOF
            self.advance()

        elif self.current_character == ":":  # colon
            symbol.type = self.COLON
            self.advance()
        elif self.current_character == "{": #  exclamation
            symbol.type = self.LEFT_CURLY
            self.advance()

        elif self.current_character == "}":
            symbol.type = self.RIGHT_CURLY
            self.advance()

        else:  # not a valid character
            self.advance()

        #  Record the current line and position in the symbol.
        symbol.line = self.location()[0]
        symbol.position = self.location()[1]

        return symbol
