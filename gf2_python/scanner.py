"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from errors import Error
import sys


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
    get_name(self): Return the next name string in the file.

    get_number(self): Return the next number in the file.

    advance(self): Read the next character of the input file and place it
                   in current_character.

    skip_spaces(self): Advance until the current character is not whitespace.

    skip_comment(self): Skip any single-line or multi-line comments.

    close_file(self): Close the file currently in use by the scanner.

    location(self): Return the current line and position within the file.

    print_location(self, symbol, option): Given a symbol, print either the
                                          current or previous symbol's line
                                          number, the line itself and symbol
                                          position, indicated by a caret under
                                          its final character on the line
                                          below. Create an error object and add
                                          to it this information for use
                                          by the GUI.

    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""
        #  Open the file.

        if path.endswith(".txt"):
            try:
                self.file = open(path)
            except FileNotFoundError:
                print('File does not exist.')
                sys.exit()
        else:
            print("Invalid file type.")
            sys.exit()

        self.error_list = []

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
                              "initial", "period", "inputs", "sequence"]
        self.logic_type_list = ["CLOCK", "SWITCH", "AND", "NAND",
                                "OR", "NOR", "DTYPE", "XOR", "SIGGEN"]
        self.input_pin_list = ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8",
                               "I9", "I10", "I11", "I12", "I13", "I14", "I15",
                               "I16", "DATA", "CLK", "SET", "CLEAR"]
        self.output_pin_list = ["Q", "QBAR"]

        #  Assign keywords an id using the "Names" module's "lookup" function.
        [self.DEVICES_ID, self.CONNECT_ID, self.MONITOR_ID,
         self.END_ID, self.initial_ID, self.period_ID,
         self.inputs_ID, self.sequence_ID] = self.names.lookup(
            self.keywords_list)
        self.current_character = self.file.read(1)

    def get_name(self):
        """Seek the next name string in input_file.

        Return the name string (or None) and place the next non-alphanumeric
        character in current_character.
        """
        name = []

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
        """Read the next character from input_file.

        Place it in current_character.
        """
        self.current_character = self.file.read(1)

    def skip_spaces(self):
        """Call advance until current_character is not whitsepace."""
        while self.current_character.isspace():
            self.advance()

    def skip_comment(self):
        """Skip single line comments and closed-comments."""
        comment_symbol = Symbol()

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
                        print("ERROR: EOF reached. Comment not closed "
                              "correctly. Missing '*'.")
                        comment_symbol.line = self.location()[0]
                        comment_symbol.position = self.location()[1]
                        curr_err = self.print_location(comment_symbol)
                        curr_err.msg = ("ERROR: EOF reached. Comment not "
                                        "closed correctly. Missing '*'.")
                        self.error_list.append(curr_err)
                        break
                    self.advance()
                self.advance()
                #  Comment closed so advance and skip spaces.
                if self.current_character == "/":
                    self.advance()
                #  Comment not closed correctly as "/" is missing.
                elif not self.current_character == "/":
                    print("ERROR: Comment terminated incorrectly. "
                          "Missing '/'.")
                    comment_symbol.line = self.location()[0]
                    comment_symbol.position = self.location()[1]
                    curr_err = self.print_location(comment_symbol)
                    curr_err.msg = ("ERROR: Comment terminated incorrectly. "
                                    "Missing '/'.")
                    self.error_list.append(curr_err)

            #  Closed comment missing "*" to start.
            else:
                print("Forward slash skipped but adjacent '*' not found "
                      "(closed comment not started).")
                comment_symbol.line = self.location()[0]
                comment_symbol.position = self.location()[1]
                curr_err = self.print_location(comment_symbol)
                curr_err.msg = ("Forward slash skipped but adjacent '*' not "
                                "found (closed comment not started).")
                self.error_list.append(curr_err)

        self.skip_spaces()

    def close_file(self):
        """Close the current file open in the scanner."""
        self.file.close()

    def location(self):
        """Return the current line and position within the file."""
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
        """Print the line that the passed symbol is on.

        Print caret on the line below to indicate the final
        character of the symbol.
        """
        error_object = Error()  # Create an error object for population.
        stored_position = self.file.tell()  # Store the current position.

        self.file.seek(0)  # Return to the beginning of the file.

        marker = 0  # Set a counter to zero.

        #  User wants to print the current symbol's line and position.
        if option is False:
            for line in self.file:
                marker += 1
                if marker == symbol.line:
                    #  store in error object:
                    error_object.line_num = "Line " + str(symbol.line) + ":"
                    error_object.line = line.replace("\n", "")
                    error_object.caret_pos = (symbol.position-2)*" " + "^"
                    #  Print error parameters:
                    print("Line " + str(symbol.line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.position-2)*" " + "^")

        #  User wants to print the last symbol's line and position.
        elif option is True:
            for line in self.file:
                marker += 1
                if marker == symbol.prev_line:
                    #  store in error object:
                    error_object.line_num = ("Line " + str(symbol.prev_line) +
                                             ":")
                    error_object.line = line.replace("\n", "")
                    error_object.caret_pos = (symbol.prev_position-2)*" " + "^"
                    #  Print error parameters:
                    print("Line " + str(symbol.prev_line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.prev_position-2)*" " + "^")

        #  Return to the stored (current) position.
        self.file.seek(stored_position)

        return error_object  # Return the error object for use by GUI.

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
        elif self.current_character == "{":  # left curly
            symbol.type = self.LEFT_CURLY
            self.advance()

        elif self.current_character == "}":  # right curly
            symbol.type = self.RIGHT_CURLY
            self.advance()

        else:  # not a valid character
            self.advance()

        #  Record the current line and position in the symbol.
        symbol.line = self.location()[0]
        symbol.position = self.location()[1]

        return symbol
