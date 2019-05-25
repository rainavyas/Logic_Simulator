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


    def __init__(self,  names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        # Initialise current symbol
        self.symbol = Symbol()

        #Initisalised error counter
        self.error_count = 0

        # Define all Syntax Errors
        [self.NO_END, self.NO_SEMICOLON_DEVICE,
        self.NEED_DEVICE_KEYWORD, self.NO_SEMICOLON_CONNECT,
        self.NEED_CONNECT_KEYWORD, self.NO_SEMICOLON_MONITOR,
        self.NEED_MONITOR_KEYWORD, self.INTEGER,
        self.NEED_QUALIFIER, self.NEED_PARAM,
        self.NO_DEVICE_SEMICOLON, self.NO_DEVICE_COLON,
        self.DEVICE_NAME, self.LOGIC_GATE,
        self.OUTPUT_PIN, self.NO_CONNECT_SEMICOLON,
        self.INPUT_PIN, self.PERIOD_INPUT_PIN,
        self.NAME_INPUT, self.ASSIGNMENT,
        self.NAME_STRING,
        self.NO_MONITOR_SEMICOLON]= self.names.unique_error_codes(22)


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
            self.error(self.NO_END, [])


        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        return True

    def error(self, error_ID, stopping_symbols, symbol_IDs = []):
        """ Display Error and recover to a useful parsing position"""

        # Increment Error Counter
        self.error_count += 1

        #Consider Syntax Errors

        if error_ID == self.NO_END:
            print("'END' keyword required at end of file")
        elif error_ID == self.NO_SEMICOLON_DEVICE:
            print("Semicolon needed after 'DEVICE'")
        elif error_ID == self.NEED_DEVICE_KEYWORD:
            print("'DEVICE' keyword required")
        elif error_ID == self.NO_SEMICOLON_CONNECT:
            print("Semicolon needed after 'CONNECT'")
        elif error_ID == self.NEED_CONNECT_KEYWORD:
            print("'CONNECT' keyword required")
        elif error_ID == self.NO_SEMICOLON_MONITOR:
            print("Semicolon needed after 'MONITOR'")
        elif error_ID == self.NEED_MONITOR_KEYWORD:
            print("'MONITOR' keyword required")
        elif error_ID == self.INTEGER:
            print("Needs to be a positive integer")
        elif error_ID == self.NEED_QUALIFIER:
            print("Parameter has to be 'initial', 'inputs' or 'period'")
        elif error_ID == self.NEED_PARAM:
            print("Comma has to followed by parameter speficification")
        elif error_ID == self.NO_DEVICE_SEMICOLON:
            print("Device definition needs to end in ';'")
        elif error_ID == self.NO_DEVICE_COLON:
            print("Device name has to be followed by ':'")
        elif error_ID == self.DEVICE_NAME:
            print("Valid Device name required")
        elif error_ID == self.LOGIC_GATE:
            print("Valid Logic gate required e.g. 'AND'")
        elif error_ID == self.OUTPUT_PIN:
            print("Output pin has to be 'Q' or 'QBAR'")
        elif error_ID == self.NO_CONNECT_SEMICOLON:
            print("Connection has to be terminated by ';'")
        elif error_ID == self.INPUT_PIN:
            print("Valid input pin required")
        elif error_ID == self.PERIOD_INPUT_PIN:
            print("'.' required to specify input pin")
        elif error_ID == self.NAME_INPUT:
            print("Name string of input device required")
        elif error_ID == self.ASSIGNMENT:
            print("'=' Assignment operator requried")
        elif error_ID == self.NAME_STRING:
            print("Valid string name required")
        elif error_ID == self.NO_MONITOR_SEMICOLON:
            print("Monitor point has to be terminated by ';'")

        #Consider Semantic Errors

        elif error_ID == self.devices.DEVICE_PRESENT:
            print("Device Name already used")

        # Display Error position
        self.scanner.print_location(self.symbol)


        # Return to recovery point for syntax errors

        #Define list of error IDs for which punctuation termination should not be moved on from
        dont_move_err_IDS = [self.INTEGER, self.NEED_PARAM, self.LOGIC_GATE, self.NEED_QUALIFIER]

        #Define a move_on Boolean state
        move_on = True

        if(self.symbol.type == self.scanner.KEYWORD):
            if (self.symbol.id in symbol_IDs):
                move_on = False
            else:
                move_on = True
        else:
            move_on = self.symbol.type not in stopping_symbols and self.symbol.type != self.scanner.EOF
            if ((not move_on) and self.symbol.type != self.scanner.NAME) :
                # Move on once more after terminating punctuation
                # Only move on for certain error types
                if error_ID not in dont_move_err_IDS:
                    self.symbol = self.scanner.get_symbol()

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
                if ((not move_on) and self.symbol.type != self.scanner.NAME) :
                    # Move on once more after terminating punctuation
                    # Only move on for certain error types
                    if error_ID not in dont_move_err_IDS:
                        self.symbol = self.scanner.get_symbol()

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
                self.error(self.NO_SEMICOLON_DEVICE, [self.scanner.KEYWORD], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
        else:
            # Error Type: 2: 'DEVICE' keyword required
            # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(self.NEED_DEVICE_KEYWORD, [self.scanner.KEYWORD], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])

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
                self.error(self.NO_SEMICOLON_CONNECT, [self.scanner.KEYWORD], [self.scanner.MONITOR_ID, self.scanner.END_ID])

        else:
            # Error Type: 4: 'CONNECT' keyword required
            # Stopping Symbols: MONITOR' or 'END' KEYWORD
            self.error(self.NEED_CONNECT_KEYWORD, [self.scanner.KEYWORD], [self.scanner.MONITOR_ID, self.scanner.END_ID])

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
                self.error(self.NO_SEMICOLON_MONITOR, [self.scanner.KEYWORD], [self.scanner.END_ID])
        else:
            # Error Type: 6: 'MONITOR' keyword required
            # Stopping Symbols: END' KEYWORD
            self.error(self.NEED_MONITOR_KEYWORD, [self.scanner.KEYWORD], [self.scanner.END_ID])

    def device(self):
        """Parse the device syntax"""

        if (self.symbol.type == self.scanner.NAME):
            device_name = self.names.get_name_string(self.symbol.id)
            device_id = self.names.query(device_name)
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.COLON):
                self.symbol = self.scanner.get_symbol()
                device_kind = self.logictype()

                if(self.symbol.type == self.scanner.COMMA):
                    self.symbol = self.scanner.get_symbol()
                    if(self.symbol.type == self.scanner.KEYWORD):
                        if(self.symbol.id == self.scanner.initial_ID or (self.symbol.id == self.scanner.inputs_ID or self.symbol.id == self.scanner.period_ID)):
                            self.symbol = self.scanner.get_symbol()

                            if(self.symbol.type == self.scanner.NUMBER):
                                device_property = int(self.names.get_name_string(self.symbol.id))
                                self.symbol = self.scanner.get_symbol()
                            else:
                                # Error type: 7: Needs to be a positive integer
                                # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                                self.error(self.INTEGER, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
                        else:
                            # Error type: 8: Parameter has to be 'initial', 'inputs' or 'period'
                            # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                            self.error(self.NEED_QUALIFIER, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
                    else:
                        # Error type: 9: Comma has to be followed by parameter speficification
                        # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                        self.error(self.NEED_PARAM, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
                if (self.symbol.type == self.scanner.SEMICOLON):
                    self.symbol = self.scanner.get_symbol()
                else:
                    #Error Type: 10: Device definition needs to end in ';'
                    # Stopping symbols: NAME, ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                    self.error(self.NO_DEVICE_SEMICOLON, [self.scanner.KEYWORD, self.scanner.SEMICOLON, self.scanner.NAME], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
            else:
                # Error Type: 11: Device name has to be followed by ':'
                # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                self.error(self.NO_DEVICE_COLON, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
        else:
            # Error Type: 12: Valid Device name required
            # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(self.DEVICE_NAME, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])

        # Check for device semantic errors
        if self.error_count == 0:
            # Only check for semantic errors if no errors so far
            err = self.devices.make_device(device_id, device_kind, device_property)
            if err != self.devices.NO_ERROR:
                # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
                self.error(err, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])

    def logictype(self):
        """Parse the type syntax in EBNF"""

        if (self.symbol.type == self.scanner.LOGIC_TYPE):
            device_kind = self.names.get_name_string(self.symbol.id)
            self.symbol = self.scanner.get_symbol()
            return device_kind
        else:
            #Error Type: 13: Valid Logic gate required e.g. 'AND'
            # Stopping symbols: ';' , 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(self.LOGIC_GATE, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID, self.scanner.END_ID])
            return None

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
                    # Stopping symbols: ';' , '=', 'MONITOR' or 'END' KEYWORD
                    self.error(self.OUTPUT_PIN, [self.scanner.KEYWORD, self.scanner.SEMICOLON. self.scanner.EQUALS], [self.scanner.MONITOR_ID, self.scanner.END_ID])

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
                                # Stopping symbols: NAME, ';' , 'MONITOR' or 'END' KEYWORD
                                self.error(self.NO_CONNECT_SEMICOLON, [self.scanner.KEYWORD, self.scanner.SEMICOLON, self.scanner.NAME], [self.scanner.MONITOR_ID, self.scanner.END_ID])
                        else:
                            # Error Type: 16: Valid input pin required
                            # Stopping symbols: ';' , 'MONITOR' or 'END' KEYWORD
                            self.error(self.INPUT_PIN, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.MONITOR_ID, self.scanner.END_ID])
                    else:
                        # Error Type: 17: Period required to specify input pin
                        # Stopping symbols: ';' , 'MONITOR' or 'END' KEYWORD
                        self.error(self.PERIOD_INPUT_PIN, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.MONITOR_ID, self.scanner.END_ID])
                else:
                    #Error Type: 18: Name string of input device required
                    # Stopping symbols: ';' , 'MONITOR' or 'END' KEYWORD
                    self.error(self.NAME_INPUT, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.MONITOR_ID, self.scanner.END_ID])
            else:
                #Error Type: 19: '=' Assignment operator requried
                # Stopping symbols: ';' , 'MONITOR' or 'END' KEYWORD
                self.error(self.ASSIGNMENT, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.MONITOR_ID, self.scanner.END_ID])
        else:
            #Error Type: 20: Valid string name required
            # Stopping symbols: ';' , 'MONITOR' or 'END' KEYWORD
            self.error(self.NAME_STRING, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.MONITOR_ID, self.scanner.END_ID])

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
                    # Stopping symbols: ';' or 'END' KEYWORD
                    self.error(self.OUTPUT_PIN, [self.scanner.KEYWORD, self.scanner.SEMICOLON], [self.scanner.END_ID])

            if(self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
            else:
                # Error Type: 21: Monitor point has to be terminated by ';'
                # Stopping symbols: 'NAME', ';' or 'END' KEYWORD
                self.error(self.NO_MONITOR_SEMICOLON, [self.scanner.KEYWORD, self.scanner.SEMICOLON, self.scanner.NAME], [self.scanner.END_ID])


# Rough Testing
path = 'test_def_file.txt'
my_names = Names()
my_scanner = Scanner(path, my_names)
my_parser = Parser(my_scanner)

my_parser.parse_network()
