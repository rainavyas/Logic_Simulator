"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from scanner import Symbol
from names import Names
from scanner import Scanner


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.
    """

    # def __init__(self, names, devices, network, monitors, scanner):
    #     """Initialise constants."""
    #     self.names = names
    #     self.devices = devices
    #     self.network = network
    #     self.monitors = monitors
    #     self.scanner = scanner
    #
    #     # Initialise current symbol
    #     self.symbol = Symbol()

    def __init__(self,  scanner):
        """Initialise constants."""
        self.scanner = scanner

        # Initialise current symbol
        self.symbol = Symbol()

        #Define all the error types and associated messages
        #Index is the error type ID
        self.err_msgs = ["'END' keyword required at end of file",
                    "Semicolon needed after 'DEVICE'",
                    "'DEVICE' keyword required",
                    "Semicolon needed after 'CONNECT'",
                    "'CONNECT' keyword required",
                    "Semicolon needed after 'MONITOR'",
                    "'MONITOR' keyword required",
                    "Needs to be an integer",
                    "Parameter has to be 'initial', 'inputs' or 'period'",
                    "Comma has to followed by parameter speficification",
                    "Device definition needs to end in ';'",
                    "Device name has to be followed by ':'",
                    "Valid Device name required",
                    "Valid Logic gate required e.g. 'AND'",
                    "Output pin has to be 'Q' or 'QBAR'",
                    "Connection has to be terminated by ';'",
                    "Valid input pin required",
                    "Period required to specify input pin",
                    "Name string of input device required",
                    "'=' Assignment operator requried",
                    "Valid string name required",
                    "Monitor point has to be terminated by ';'"]

    def parse_network(self):
        """Parse the circuit definition file."""

        #Get the first symbol from Scanner
        self.symbol = self.scanner.get_symbol()

        #Main structure
        self.devicelist()
        self.connectlist()
        self.monitorlist()

        if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID):
            # Error Type: 0: 'END' keyword required at end of file
            self.error(0, None)


        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True

    def error(self, error_ID, stopping_symbols, symbol_IDs = []]):
        """ Display Error and recover to a useful parsing position"""

        # Display Error
        print("SYNTAX ERROR:")
        err_msg = self.err_msgs[error_ID]
        print(err_msg)
        self.scanner.print_location(self.symbol)

        # Return to recovery point

        #Define a move_on Boolean state
        move_on = True

        if(self.symbol.type == self.scanner.KEYWORD):
            if (self.symbol.id in symbol_IDs):
                move_on = False
            else:
                move_on = True
        else:
            move_on = self.symbol.type not in stopping_symbols and self.symbol.type != self.scanner.EOF


        while (move_on):
            self.symbol = self.scanner.get_symbol()

            # Update move_on Boolean state
            if(self.symbol.type == self.scanner.KEYWORD):
                if (self.symbol.id in symbol_IDs):
                    move_on = False
                else:
                    move_on = True
            else:
                move_on = self.symbol.type not in stopping_symbols and self.symbol.type != self.scanner.EOF

    def devicelist(self):
        """Parse the devices section"""

        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
                self.device()
                while (self.symbol.type == self.scanner.NAME):
                    self.device()
            else:
                # Error Type: 1: Semicolon needed after 'DEVICE'
                # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END' KEYWORD
                self.error(1, [self.scanner.KEYWORD], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
        else:
            # Error Type: 2: 'DEVICE' keyword required
            # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(2, [self.scanner.KEYWORD], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])


    def connectlist(self):
        """Parse the connections section"""

        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID):
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()

                while (self.symbol.type == self.scanner.NAME):
                    self.connection()
            else:
                # Error Type: 3: Semicolon needed after 'CONNECT'
                # Stopping Symbols: MONITOR' or 'END' KEYWORD
                self.error(3, [self.scanner.KEYWORD], [self.scanner.MONITOR_ID, self.scanner.END_ID])

        else:
            # Error Type: 4: 'CONNECT' keyword required
            # Stopping Symbols: MONITOR' or 'END' KEYWORD
            self.error(4, [self.scanner.KEYWORD], [self.scanner.MONITOR_ID, self.scanner.END_ID])

    def monitorlist(self):
        """Parse the monitoring section"""

        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.MONITOR_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
                self.monitor_point()
                while (self.symbol.type == self.scanner.NAME):
                    self.monitor_point()
            else:
                # Error Type: 5: Semicolon needed after 'MONITOR'
                # Stopping Symbols: END' KEYWORD
                self.error(5, [self.scanner.KEYWORD], [self.scanner.END_ID])
        else:
            # Error Type: 6: 'MONITOR' keyword required
            # Stopping Symbols: END' KEYWORD
            self.error(6, [self.scanner.KEYWORD], [self.scanner.END_ID])

    def device(self):
        """Parse the device syntax"""

        if (self.symbol.type == self.scanner.NAME):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.COLON):
                self.symbol = self.scanner.get_symbol()
                self.logictype()

                if(self.symbol.type == self.scanner.COMMA):
                    self.symbol = self.scanner.get_symbol()
                    if(self.symbol.type == self.scanner.KEYWORD):
                        if(self.symbol.id == self.scanner.initial_ID or (self.symbol.id == self.scanner.inputs_ID or self.symbol.id == self.scanner.period_ID)):
                            self.symbol = self.scanner.get_symbol()

                            if(self.symbol.type == self.scanner.NUMBER):
                                self.symbol = self.scanner.get_symbol()
                            else:
                                # Error type: 7: Needs to be an integer
                                # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                                self.error(7, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
                        else:
                            # Error type: 8: Parameter has to be 'initial', 'inputs' or 'period'
                            self.error()

                    else:
                        # Error type: 9: Comma has to be followed by parameter speficification
                        # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                        self.error(9, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
                if (self.symbol.type == self.scanner.SEMICOLON):
                    self.symbol = self.scanner.get_symbol()
                else:
                    #Error Type: 10: Device definition needs to end in ';'
                    # Stopping symbols: NAME, ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                    self.error(10, [self.scanner.KEYWORD, self.scanner.SEMICOLON, self.scanner.NAME], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
            else:
                # Error Type: 11: Device name has to be followed by ':'
                # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                self.error(11, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
        else:
            # Error Type: 12: Valid Device name required
            # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(12, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])

    def logictype(self):
        """Parse the type syntax in EBNF"""

        if (self.symbol.type == self.scanner.LOGIC_TYPE):
            self.symbol = self.scanner.get_symbol()
        else:
            #Error Type: 13: Valid Logic gate required e.g. 'AND'
            # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(13, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])

    def connection(self):
        """Parse the connection syntax in EBNF"""

        if (self.symbol.type == self.scanner.NAME):
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.PERIOD):
                self.symbol = self.scanner.get_symbol()

                if(self.symbol.type == self.scanner.OUT_PIN):
                    self.symbol = self.scanner.get_symbol()
                else:
                    #Error Type: 14: Output pin has to be 'Q' or 'QBAR'
                    self.error()

            if (self.symbol.type == self.scanner.EQUALS):
                self.symbol = self.scanner.get_symbol()

                if (self.symbol.type == self.scanner.NAME):
                    self.symbol = self.scanner.get_symbol()

                    if (self.symbol.type == self.scanner.PERIOD):
                        self.symbol = self.scanner.get_symbol()

                        if(self.symbol.type == self.scanner.IN_PIN):
                            self.symbol = self.scanner.get_symbol()

                            if(self.symbol.type == self.scanner.SEMICOLON):
                                self.symbol = self.scanner.get_symbol()
                            else:
                                # Error Type: 15: Connection has to be terminated by ';'
                                self.error()
                        else:
                            # Error Type: 16: Valid input pin required
                            self.error()
                    else:
                        # Error Type: 17: Period required to specify input pin
                        self.error()
                else:
                    #Error Type: 18: Name string of input device required
                    self.error()
            else:
                #Error Type: 19: '=' Assignment operator requried
                self.error()
        else:
            #Error Type: 20: Valid string name required
            self.error()


    def monitor_point(self):
        """Parse the monitor_point in EBNF"""

        if (self.symbol.type == self.scanner.NAME):
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.PERIOD):
                self.symbol = self.scanner.get_symbol()

                if(self.symbol.type == self.scanner.OUT_PIN):
                    self.symbol = self.scanner.get_symbol()
                else:
                    #Error Type: 14: Output pin has to be 'Q' or 'QBAR'
                    self.error()

            if(self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
            else:
                # Error Type: 21: Monitor point has to be terminated by ';'
                self.error()


# Rough Testing
path = 'test_def_file.txt'
my_names = Names()
my_scanner = Scanner(path, my_names)
my_parser = Parser(my_scanner)

my_parser.parse_network()

"""Defining all the error types and their messages:


"""
