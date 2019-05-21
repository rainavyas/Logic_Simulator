"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from scanner import Symbol


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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        # Initialise current symbol
        self.symbol = Symbol()

    def parse_network(self):
        """Parse the circuit definition file."""

        #Get the first symbol from Scanner
        self.symbol = self.scanner.get_symbol()

        #Main structure
        self.devicelist()
        self.connectlist()
        self.monitorlist()

        if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.END_ID):
            self.error()


        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True

    def error(self):
        print("We have a syntax error")

    def devicelist(self):
        """Parse the devices section"""

        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
                self.device()
                while not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == self.scanner.CONNECT_ID):
                    self.device()
            else:
                self.error()
        else:
            self.error()


    def connectlist(self):
        """Parse the connections section"""

    def monitorlist(self):
        """Parse the monitoring section"""

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
                                # Error type: needs to be an integer
                                self.error()
                        else:
                            # Error type: Parameter has to be initial, inputs or period
                            self.error()

                    else:
                        # Error type: Comma has to followed by parameter speficification
                        self.error()
                if (self.symbol.type == self.scanner.SEMICOLON):
                    self.symbol = self.scanner.get_symbol()
                else:
                    #Error Type: needs to end in ';'
                    self.error()
            else:
                # Error Type: Device name has to be followed by ':'
                self.error()
        else:
            # Error Type: Valid Device name required
            self.error()

    def logictype(self):
        """Parse the type syntax in EBNF"""
