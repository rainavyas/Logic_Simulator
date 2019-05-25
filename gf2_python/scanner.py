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
        self.prev_line = None
        self.position = None
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
        self.file = open(path)

        self.names = names
        self.symbol_type_list = [self.COMMA, self.SEMICOLON, self.EQUALS,
                                 self.KEYWORD, self.LOGIC_TYPE, self.OUT_PIN,
                                 self.IN_PIN, self.NUMBER, self.NAME,
                                 self.PERIOD, self.COLON, self.EOF] = range(12)

        self.keywords_list = ["DEVICES", "CONNECT", "MONITOR", "END",
                              "initial", "period", "inputs"]
        self.logic_type_list = ["CLOCK", "SWITCH", "AND", "NAND",
                                "OR", "NOR", "DTYPE", "XOR"]
        self.input_pin_list = ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8",
                               "I9", "I10", "I11", "I12", "I13", "I14", "I15",
                               "I16", "DATA", "CLK", "SET", "CLEAR"]
        self.output_pin_list = ["Q", "QBAR"]

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
            self.skip_spaces()
            self.advance()

        #  Skip closed comments.
        if self.current_character == "/":
            self.advance()
            if self.current_character == "*":
                self.advance()
                while not self.current_character == "*":
                    if self.current_character == "":
                        print("""ERROR: EOF reached. Comment not closed
                              correctly. Missing '*'.""")
                        break
                    self.advance()
                self.advance()
                if self.current_character == "/":
                    self.advance()
                    self.skip_spaces()
                elif not self.current_character == "/":
                    print("""ERROR: Comment terminated incorrectly.
                          Missing '/'.""")
                    comment_symbol = Symbol()
                    comment_symbol.line = self.location()[0]
                    comment_symbol.position = self.location()[1]
                    self.print_location(comment_symbol)
            else:
                print("""Forward slash skipped but adjacent '*' not found
                      (closed comment not started).""")

    def location(self):
        """Print the current input line along with a marker showing symbol
        position in the line
        """
        stored_position = self.file.tell()

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

        current_line = ''
        current_position = ''

        self.file.seek(stored_position)


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

    def print_location(self, symbol, option = False):
        """ Add correct documentation here.
        """

        stored_position = self.file.tell()

        self.file.seek(0)

        marker = 0

        if option == False:
            for line in self.file:
                marker += 1
                if marker == symbol.line:
                    print("Line " + str(symbol.line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.position-2)*" " + "^")

        elif option == True:
            for line in self.file:
                marker += 1
                if marker == symbol.prev_line:
                    print("Line " + str(symbol.prev_line) + ":")
                    print(line.replace("\n", ""))
                    print((symbol.prev_position-2)*" " + "^")

        self.file.seek(stored_position)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol.

        Break if 'END' reached.
        """

        symbol = Symbol()
        symbol.prev_line = self.location()[0]
        symbol.prev_position = self.location()[1]

        self.skip_spaces()  # current character now not whitespace
        self.skip_comment()  # current character now not comment

        if self.current_character.isalpha():  # name
            name_string = self.get_name()
            # print("Name_string:", name_string)
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
            # print("First number is:", self.current_character)
            symbol.id = self.names.lookup(self.get_number())
            symbol.type = self.NUMBER

        elif self.current_character == "=":  # equals
            # print("Found an equals")
            symbol.type = self.EQUALS
            self.advance()

        elif self.current_character == ",":  # comma
            # print("Found a comma")
            symbol.type = self.COMMA
            self.advance()

        elif self.current_character == ";":  # semicolon
            # print("Found a semi-colon")
            symbol.type = self.SEMICOLON
            self.advance()

        elif self.current_character == ".":  # period
            # print("Found a period")
            symbol.type = self.PERIOD
            self.advance()

        elif self.current_character == "":  # end of file
            # print("Found EOF")
            symbol.type = self.EOF
            self.advance()

        elif self.current_character == ":":  # colon
            # print("Found colon")
            symbol.type = self.COLON
            self.advance()

        else:  # not a valid character
            self.advance()

        symbol.line = self.location()[0]
        symbol.position = self.location()[1]

        return symbol

# path_test = os.getcwd() + "/(temp)text_file.txt"
# names_test = Names()
# scanner = Scanner(path_test, names_test)
#
# for n in range(30):
#     Test_symbol = scanner.get_symbol()
#     scanner.print_location(Test_symbol)
#     print(' ')
