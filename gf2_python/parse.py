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
from monitors import Monitors
from devices import Devices
from network import Network


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

    error(self, error_ID, stopping_symbols, symbol_IDs = []): Display error and
                                    and recover to a useful parsing position
    devicelist(self): Parse the devices section

    connectlist(self): Parse the connections section

    monitorlist(self): Parse the monitoring section

    device(self): Parse the device syntax

    logictype(self): Parse the type syntax and the return the type of the
                     current device

    connection(self): Parse the connection syntax

    monitor_point(self): Parse the monitor_point syntax

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

        # Initisalise a historic symbol for error location reporting
        self.old_symbol = Symbol()

        # Initisalise error counter
        self.error_count = 0

        # Initialise an input pin counter
        self.num_input_pin = 0

        # Define all Syntax Errors
        [self.NO_END, self.NO_CURLY_DEVICE,
         self.NEED_DEVICE_KEYWORD, self.NO_CURLY_CONNECT,
         self.NEED_CONNECT_KEYWORD, self.NO_CURLY_MONITOR,
         self.NEED_MONITOR_KEYWORD, self.INTEGER,
         self.NEED_QUALIFIER, self.NEED_PARAM,
         self.NO_DEVICE_SEMICOLON, self.NO_DEVICE_COLON,
         self.DEVICE_NAME, self.LOGIC_GATE,
         self.OUTPUT_PIN, self.NO_CONNECT_SEMICOLON,
         self.INPUT_PIN, self.PERIOD_INPUT_PIN,
         self.NAME_INPUT, self.ASSIGNMENT,
         self.NAME_STRING, self.MISSING_RIGHT_CURLY,
         self.NO_MONITOR_SEMICOLON,
         self.FLOATING_INPUT_PIN] = self.names.unique_error_codes(24)

    def parse_network(self):
        """Parse the circuit definition file."""

        # Get the first symbol from Scanner
        self.symbol = self.scanner.get_symbol()

        # Main structure
        self.devicelist()
        self.connectlist()
        self.monitorlist()

        if not (self.symbol.type == self.scanner.KEYWORD
                and self.symbol.id == self.scanner.END_ID):
            # Error Type: 0: 'END' keyword required at end of file
            self.error(self.NO_END, [])

        if self.error_count == 0:
            return True
        else:
            # Reset all classes for GUI
            self.names = Names()
            self.devices = Devices(self.names)
            self.network = Network(self.names, self.devices)
            self.monitors = Monitors(self.names, self.devices, self.network)

            return False

    def error(self, error_ID, stopping_symbols, symbol_IDs=[]):
        """ Display Error and recover to a useful parsing position"""

        # Increment Error Counter
        self.error_count += 1

        # Consider Syntax Errors
        if error_ID == self.NO_END:
            msg = "'END' keyword required at end of file"
            option = False
        elif error_ID == self.NO_CURLY_DEVICE:
            msg = "Expected '{' after 'DEVICES'"
            option = True
        elif error_ID == self.NEED_DEVICE_KEYWORD:
            msg = "'DEVICES' keyword required"
            option = False
        elif error_ID == self.NO_CURLY_CONNECT:
            msg = "Expected '{' after 'CONNECT'"
            option = True
        elif error_ID == self.NEED_CONNECT_KEYWORD:
            msg = "'CONNECT' keyword required"
            option = False
        elif error_ID == self.NO_CURLY_MONITOR:
            msg = "Expected '{' after 'MONITOR'"
            option = True
        elif error_ID == self.NEED_MONITOR_KEYWORD:
            msg = "'MONITOR' keyword required"
            option = False
        elif error_ID == self.INTEGER:
            msg = "Needs to be a positive integer"
            option = False
        elif error_ID == self.NEED_QUALIFIER:
            msg = "Expected a parameter: 'initial', 'inputs' or 'period'"
            option = False
        elif error_ID == self.NEED_PARAM:
            msg = "Comma has to followed by parameter specification"
            option = False
        elif error_ID == self.NO_DEVICE_SEMICOLON:
            msg = "Device definition needs to end in ';'"
            option = True
        elif error_ID == self.NO_DEVICE_COLON:
            msg = "Device name has to be followed by ':'"
            option = True
        elif error_ID == self.DEVICE_NAME:
            msg = "Valid Device name required"
            option = False
        elif error_ID == self.LOGIC_GATE:
            msg = "Valid Logic gate required e.g. 'AND'"
            option = False
        elif error_ID == self.OUTPUT_PIN:
            msg = "Output pin has to be 'Q' or 'QBAR'"
            option = False
        elif error_ID == self.NO_CONNECT_SEMICOLON:
            msg = "Connection has to be terminated by ';'"
            option = True
        elif error_ID == self.INPUT_PIN:
            msg = "Valid input pin required"
            option = False
        elif error_ID == self.PERIOD_INPUT_PIN:
            msg = "'.' required to specify input pin"
            option = True
        elif error_ID == self.NAME_INPUT:
            msg = "Name string of input device required"
            option = True
        elif error_ID == self.ASSIGNMENT:
            msg = "'=' Assignment operator requried"
            option = True
        elif error_ID == self.NAME_STRING:
            msg = "Valid string name required"
            option = False
        elif error_ID == self.NO_MONITOR_SEMICOLON:
            msg = "Monitor point has to be terminated by ';'"
            option = True
        elif error_ID == self.MISSING_RIGHT_CURLY:
            msg = "Missing '}'"
            option = True

        # Consider Semantic Errors
        # DEVICES
        elif error_ID == self.devices.DEVICE_PRESENT:
            msg = "Device Name already used"
            option = False
            self.symbol = self.old_symbol
        elif error_ID == self.devices.NO_QUALIFIER:
            msg = "Device qualifier required"
            option = True
        elif error_ID == self.devices.INVALID_QUALIFIER:
            msg = "Valid device qualifier requried"
            option = True
        elif error_ID == self.devices.QUALIFIER_PRESENT:
            msg = "Qualifier already present"
            option = True
        elif error_ID == self.devices.BAD_DEVICE:
            msg = "Invalid device declared"
            option = True

        # CONNECTIONS
        elif error_ID == self.network.DEVICE_ABSENT:
            msg = "Device is not declared"
            option = False
            self.symbol = self.old_symbol
        elif error_ID == self.network.INPUT_CONNECTED:
            msg = "Input is already in a connection"
            option = True
        elif error_ID == self.network.INPUT_TO_INPUT:
            msg = "Both ports are inputs"
            option = True
        elif error_ID == self.network.PORT_ABSENT:
            msg = "Port is absent"
            option = True
        elif error_ID == self.network.OUTPUT_TO_OUTPUT:
            msg = "Both ports are outputs"
            option = True

        # MONITORING
        elif error_ID == self.monitors.NOT_OUTPUT:
            msg = "Cannot monitor a point that is not an output"
            option = True
        elif error_ID == self.monitors.MONITOR_PRESENT:
            msg = "This point is already being monitored"
            option = True

        # Floating input pins
        elif error_ID == self.FLOATING_INPUT_PIN:
            msg = "All input pins haven't been connected"
            option = True

        else:
            msg = "ERROR"
            option = True

        # Display error message
        print(msg)

        # Display Error position and get error object
        this_err = self.scanner.print_location(self.symbol, option)
        this_err.msg = msg

        # Append the error object to scanner's list of errors
        self.scanner.error_list.append(this_err)

        # Return to recovery point for syntax errors

        # Define error IDs where punctuation stopping to not be moved on from
        dont_move_err_IDS = [self.INTEGER, self.NEED_PARAM, self.LOGIC_GATE,
                             self.NEED_QUALIFIER]

        # Define a move_on Boolean state
        move_on = True

        if(self.symbol.type == self.scanner.KEYWORD):
            if (self.symbol.id in symbol_IDs):
                move_on = False
            else:
                move_on = True
        else:
            move_on = self.symbol.type not in stopping_symbols and \
                self.symbol.type != self.scanner.EOF
            if ((not move_on) and (self.symbol.type != self.scanner.NAME and
                                   self.symbol.type
                                   != self.scanner.RIGHT_CURLY)):
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
                move_on = self.symbol.type not in stopping_symbols and \
                    self.symbol.type != self.scanner.EOF
                if ((not move_on) and self.symbol.type != self.scanner.NAME):
                    # get next symbol once more after terminating punctuation
                    # Only for certain error types
                    if error_ID not in dont_move_err_IDS:
                        self.symbol = self.scanner.get_symbol()

    def devicelist(self):
        """Parse the devices section"""

        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.LEFT_CURLY):
                self.symbol = self.scanner.get_symbol()
                self.device()
                while (self.symbol.type == self.scanner.NAME):
                    self.device()
                # Check right curly bracket ends device block
                if (self.symbol.type == self.scanner.RIGHT_CURLY):
                    self.symbol = self.scanner.get_symbol()
                else:
                    if (self.symbol.type == self.scanner.KEYWORD and
                            self.symbol.id == self.scanner.CONNECT_ID):
                        # Error Type: missing '}'
                        # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END'
                        self.error(self.MISSING_RIGHT_CURLY,
                                   [self.scanner.KEYWORD],
                                   [self.scanner.CONNECT_ID,
                                    self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
                    else:
                        # Bad name terminated devices incorrectly
                        # Error type: Invalid name
                        # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END'
                        self.error(self.DEVICE_NAME, [self.scanner.KEYWORD],
                                   [self.scanner.CONNECT_ID,
                                    self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
            else:
                # Error: Left curly needed after 'DEVICE'
                # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END' KEYWORD
                self.error(self.NO_CURLY_DEVICE, [self.scanner.KEYWORD],
                           [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                            self.scanner.END_ID])
        else:
            # Error: 'DEVICE' keyword required
            # Stopping Symbols: 'CONNECT', 'MONITOR' or 'END' KEYWORD
            self.error(self.NEED_DEVICE_KEYWORD, [self.scanner.KEYWORD],
                       [self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                        self.scanner.END_ID])

    def connectlist(self):
        """Parse the connections section"""

        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CONNECT_ID):
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.LEFT_CURLY):
                self.symbol = self.scanner.get_symbol()

                while (self.symbol.type == self.scanner.NAME):
                    self.connection()
                    # Each connection decrements pin count by one
                    self.num_input_pin -= 1

                # Check right curly bracket ends connections block
                if (self.symbol.type == self.scanner.RIGHT_CURLY):
                    self.symbol = self.scanner.get_symbol()
                else:
                    if (self.symbol.type == self.scanner.KEYWORD and
                            self.symbol.id == self.scanner.MONITOR_ID):
                        # Error Type: missing '}'
                        # Stopping Symbols: MONITOR' or 'END' KEYWORD
                        self.error(self.MISSING_RIGHT_CURLY,
                                   [self.scanner.KEYWORD],
                                   [self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
                    else:
                        # Bad name terminated connections incorrectly
                        # Error type: Invalid name
                        # Stopping Symbols: MONITOR' or 'END' KEYWORD
                        self.error(self.NAME_STRING, [self.scanner.KEYWORD],
                                   [self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
            else:
                # Error: Left curly needed after 'CONNECT'
                # Stopping Symbols: MONITOR' or 'END' KEYWORD
                self.error(self.NO_CURLY_CONNECT, [self.scanner.KEYWORD],
                           [self.scanner.MONITOR_ID, self.scanner.END_ID])

        else:
            # Error: 'CONNECT' keyword required
            # Stopping Symbols: MONITOR' or 'END' KEYWORD
            self.error(self.NEED_CONNECT_KEYWORD, [self.scanner.KEYWORD],
                       [self.scanner.MONITOR_ID, self.scanner.END_ID])

        # Check all input pins have been connected
        if self.error_count == 0:
            if self.num_input_pin != 0:
                # Error: Floating inputs pins
                # Stopping Symbols: MONITOR' or 'END' KEYWORD
                self.error(self.FLOATING_INPUT_PIN, [self.scanner.KEYWORD],
                           [self.scanner.MONITOR_ID, self.scanner.END_ID])

    def monitorlist(self):
        """Parse the monitoring section"""

        if (self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.MONITOR_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.LEFT_CURLY):
                self.symbol = self.scanner.get_symbol()
                self.monitor_point()
                while (self.symbol.type == self.scanner.NAME):
                    self.monitor_point()

                # Check right curly bracket ends monitors block
                if (self.symbol.type == self.scanner.RIGHT_CURLY):
                    self.symbol = self.scanner.get_symbol()
                else:
                    if (self.symbol.type == self.scanner.KEYWORD and
                            self.symbol.id == self.scanner.END_ID):
                        # Error: missing '}'
                        # Stopping Symbols: END' KEYWORD
                        self.error(self.MISSING_RIGHT_CURLY,
                                   [self.scanner.KEYWORD],
                                   [self.scanner.END_ID])
                    else:
                        # Bad name terminated monitors incorrectly
                        # Error: Invalid name
                        # Stopping Symbols: END' KEYWORD
                        self.error(self.NAME_STRING, [self.scanner.KEYWORD],
                                   [self.scanner.END_ID])
            else:
                # Error: Curly needed after 'MONITOR'
                # Stopping Symbols: END' KEYWORD
                self.error(self.NO_CURLY_MONITOR, [self.scanner.KEYWORD],
                           [self.scanner.END_ID])
        else:
            # Error: 'MONITOR' keyword required
            # Stopping Symbols: END' KEYWORD
            self.error(self.NEED_MONITOR_KEYWORD, [self.scanner.KEYWORD],
                       [self.scanner.END_ID])

    def device(self):
        """Parse the device syntax"""

        if (self.symbol.type == self.scanner.NAME):
            device_name = self.names.get_name_string(self.symbol.id)
            device_id = self.names.query(device_name)
            self.old_symbol = self.symbol  # for reporting duplicate devices
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.COLON):
                self.symbol = self.scanner.get_symbol()
                device_kind = self.logictype()

                if(self.symbol.type == self.scanner.COMMA):
                    self.symbol = self.scanner.get_symbol()
                    if(self.symbol.type == self.scanner.KEYWORD):
                        if(self.symbol.id == self.scanner.initial_ID or
                           (self.symbol.id == self.scanner.inputs_ID or
                                self.symbol.id == self.scanner.period_ID)):

                            self.symbol = self.scanner.get_symbol()

                            if(self.symbol.type == self.scanner.NUMBER):
                                device_property = int(
                                    self.names.get_name_string(self.symbol.id))
                                self.symbol = self.scanner.get_symbol()
                            else:
                                # Error: Needs to be a positive integer
                                # Stop symbs:';','}','CONNECT','MONITOR', END
                                self.error(
                                    self.INTEGER, [
                                        self.scanner.KEYWORD,
                                        self.scanner.SEMICOLON,
                                        self.scanner.RIGHT_CURLY], [
                                        self.scanner.CONNECT_ID,
                                        self.scanner.MONITOR_ID,
                                        self.scanner.END_ID])
                        else:
                            # Error: Parameter to be 'initial', inputs, period
                            # Stopping symbols: ';' , '}','CONNECT', 'MONITOR'
                            # or 'END' KEYWORD '
                            self.error(self.NEED_QUALIFIER,
                                       [self.scanner.KEYWORD,
                                        self.scanner.SEMICOLON,
                                        self.scanner.RIGHT_CURLY],
                                       [self.scanner.CONNECT_ID,
                                        self.scanner.MONITOR_ID,
                                        self.scanner.END_ID])
                    else:
                        # Error: Comma has to be followed by parameter
                        # speficification
                        # Stopping symbols: ';' , '}', 'CONNECT', 'MONITOR'
                        # or 'END' KEYWORD
                        self.error(self.NEED_QUALIFIER, [self.scanner.KEYWORD,
                                   self.scanner.SEMICOLON,
                                   self.scanner.RIGHT_CURLY],
                                   [self.scanner.CONNECT_ID,
                                    self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
                else:
                    # There is no device property
                    device_property = None

                if (self.symbol.type == self.scanner.SEMICOLON):
                    self.symbol = self.scanner.get_symbol()
                else:
                    # Error: Device definition needs to end in ';'
                    # Stopping symbols: NAME, ';' , '}', 'CONNECT', 'MONITOR'
                    # or 'END' KEYWORD
                    self.error(self.NO_DEVICE_SEMICOLON,
                               [self.scanner.KEYWORD,
                                self.scanner.SEMICOLON,
                                self.scanner.NAME,
                                self.scanner.RIGHT_CURLY],
                               [self.scanner.CONNECT_ID,
                                self.scanner.MONITOR_ID,
                                self.scanner.END_ID])
            else:
                # Error: Device name has to be followed by ':'
                # Stopping symbols: ';' , '}', 'CONNECT', 'MONITOR' or 'END'
                # KEYWORD
                self.error(
                    self.NO_DEVICE_COLON, [
                        self.scanner.KEYWORD, self.scanner.SEMICOLON,
                        self.scanner.RIGHT_CURLY], [
                        self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                        self.scanner.END_ID])
        else:
            # Error: Valid Device name required
            # Stopping symbols: ';' , '}', 'CONNECT', 'MONITOR' or 'END'
            # KEYWORD
            self.error(
                self.DEVICE_NAME, [
                    self.scanner.KEYWORD, self.scanner.SEMICOLON,
                    self.scanner.RIGHT_CURLY], [
                    self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                    self.scanner.END_ID])

        # Check for device semantic errors
        if self.error_count == 0:
            # Only check for semantic errors if no errors so far
            err = self.devices.make_device(
                device_id, device_kind, device_property)
            if err != self.devices.NO_ERROR:
                # Stopping symbols: ';' , '}', 'CONNECT', 'MONITOR' or 'END'
                # KEYWORD
                self.error(
                    err, [
                        self.scanner.KEYWORD, self.scanner.SEMICOLON,
                        self.scanner.RIGHT_CURLY], [
                        self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                        self.scanner.END_ID])

        # Increment input pin counter by number of pins on new device
        if self.error_count == 0:
            device_name_string = self.names.get_name_string(device_kind)
            if device_name_string == "DTYPE":
                self.num_input_pin += 4
            elif device_name_string in ["AND", "OR", "NAND", "NOR"]:
                self.num_input_pin += device_property
            elif device_name_string == "XOR":
                self.num_input_pin += 2

    def logictype(self):
        """Parse the type syntax

        Return the device type of the current device"""

        if (self.symbol.type == self.scanner.LOGIC_TYPE):
            device_kind_string = self.names.get_name_string(self.symbol.id)
            device_kind = self.names.query(device_kind_string)
            self.symbol = self.scanner.get_symbol()
            return device_kind
        else:
            # Error: Valid Logic gate required e.g. 'AND'
            # Stopping symbols: ';' , '}', 'CONNECT', 'MONITOR' or 'END'
            # KEYWORD
            self.error(
                self.LOGIC_GATE, [
                    self.scanner.KEYWORD, self.scanner.SEMICOLON,
                    self.scanner.RIGHT_CURLY], [
                    self.scanner.CONNECT_ID, self.scanner.MONITOR_ID,
                    self.scanner.END_ID])
            return None

    def connection(self):
        """Parse the connection syntax"""

        if (self.symbol.type == self.scanner.NAME):
            device_name = self.names.get_name_string(self.symbol.id)
            first_device_id = self.names.query(device_name)
            self.old_symbol = self.symbol  # for undeclared device names
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.PERIOD):
                self.symbol = self.scanner.get_symbol()

                if(self.symbol.type == self.scanner.OUT_PIN):
                    pin_name = self.names.get_name_string(self.symbol.id)
                    first_port_id = self.names.query(pin_name)
                    self.symbol = self.scanner.get_symbol()
                else:
                    # Error: Output pin has to be 'Q' or 'QBAR'
                    # Stopping symbols: ';', '}' , '=', 'MONITOR' or 'END'
                    # KEYWORD
                    self.error(self.OUTPUT_PIN,
                               [self.scanner.KEYWORD,
                                self.scanner.SEMICOLON, self.scanner.EQUALS,
                                self.scanner.RIGHT_CURLY],
                               [self.scanner.MONITOR_ID,
                                self.scanner.END_ID])
            else:
                # Device with only a single output port
                first_port_id = None

            if (self.symbol.type == self.scanner.EQUALS):
                self.symbol = self.scanner.get_symbol()

                if (self.symbol.type == self.scanner.NAME):
                    device_name = self.names.get_name_string(self.symbol.id)
                    second_device_id = self.names.query(device_name)
                    self.symbol = self.scanner.get_symbol()

                    if (self.symbol.type == self.scanner.PERIOD):
                        self.symbol = self.scanner.get_symbol()

                        if(self.symbol.type == self.scanner.IN_PIN):
                            pin_name = self.names.get_name_string(
                                self.symbol.id)
                            second_port_id = self.names.query(pin_name)
                            self.symbol = self.scanner.get_symbol()

                            if(self.symbol.type == self.scanner.SEMICOLON):
                                self.symbol = self.scanner.get_symbol()
                            else:
                                # Error: Connection has to be terminated by ';'
                                # Stopping symbols: NAME, ';', '}' , 'MONITOR'
                                # or 'END' KEYWORD
                                self.error(
                                    self.NO_CONNECT_SEMICOLON, [
                                        self.scanner.KEYWORD,
                                        self.scanner.SEMICOLON,
                                        self.scanner.NAME,
                                        self.scanner.RIGHT_CURLY], [
                                        self.scanner.MONITOR_ID,
                                        self.scanner.END_ID])
                        else:
                            # Error: Valid input pin required
                            # Stopping symbols: ';' , '}', 'MONITOR' or 'END'
                            # KEYWORD
                            self.error(
                                self.INPUT_PIN, [
                                    self.scanner.KEYWORD,
                                    self.scanner.SEMICOLON,
                                    self.scanner.RIGHT_CURLY], [
                                    self.scanner.MONITOR_ID,
                                    self.scanner.END_ID])
                    else:
                        # Error: Period required to specify input pin
                        # Stopping symbols: ';' , '}', 'MONITOR' or 'END'
                        # KEYWORD
                        self.error(
                            self.PERIOD_INPUT_PIN, [
                                self.scanner.KEYWORD, self.scanner.SEMICOLON,
                                self.scanner.RIGHT_CURLY],
                            [self.scanner.MONITOR_ID, self.scanner.END_ID])
                else:
                    # Error: Name string of input device required
                    # Stopping symbols: ';' , '}', 'MONITOR' or 'END' KEYWORD
                    self.error(
                        self.NAME_INPUT, [
                            self.scanner.KEYWORD, self.scanner.SEMICOLON,
                            self.scanner.RIGHT_CURLY],
                        [self.scanner.MONITOR_ID, self.scanner.END_ID])
            else:
                # Error: '=' Assignment operator requried
                # Stopping symbols: ';' , '}', 'MONITOR' or 'END' KEYWORD
                self.error(
                    self.ASSIGNMENT, [
                        self.scanner.KEYWORD, self.scanner.SEMICOLON,
                        self.scanner.RIGHT_CURLY], [self.scanner.MONITOR_ID,
                                                    self.scanner.END_ID])
        else:
            # Error: Valid string name required
            # Stopping symbols: ';' , '}', 'MONITOR' or 'END' KEYWORD
            self.error(
                self.NAME_STRING, [
                    self.scanner.KEYWORD, self.scanner.SEMICOLON,
                    self.scanner.RIGHT_CURLY], [self.scanner.MONITOR_ID,
                                                self.scanner.END_ID])

        # Check for Connection Semantic errors
        if self.error_count == 0:
            # Only check for semantic errors if no errors so far
            err = self.network.make_connection(
                first_device_id, first_port_id,
                second_device_id, second_port_id)
            if err != self.network.NO_ERROR:
                # Stopping symbols: ';' , '}', 'MONITOR' or 'END' KEYWORD
                self.error(
                    err, [
                        self.scanner.KEYWORD, self.scanner.SEMICOLON,
                        self.scanner.RIGHT_CURLY], [self.scanner.MONITOR_ID,
                                                    self.scanner.END_ID])

    def monitor_point(self):
        """Parse the monitor_point syntax"""

        if (self.symbol.type == self.scanner.NAME):
            device_id = self.symbol.id
            self.symbol = self.scanner.get_symbol()

            if (self.symbol.type == self.scanner.PERIOD):
                self.symbol = self.scanner.get_symbol()

                if(self.symbol.type == self.scanner.OUT_PIN):
                    output_id = self.symbol.id
                    self.symbol = self.scanner.get_symbol()
                else:
                    # Error: Output pin has to be 'Q' or 'QBAR'
                    # Stopping symbols: '}', ';' or 'END' KEYWORD
                    self.error(
                        self.OUTPUT_PIN, [
                            self.scanner.KEYWORD, self.scanner.SEMICOLON,
                            self.scanner.RIGHT_CURLY], [self.scanner.END_ID])

            else:
                # Device only has one output port
                output_id = None

            if(self.symbol.type == self.scanner.SEMICOLON):
                self.symbol = self.scanner.get_symbol()
            else:
                # Error: Monitor point has to be terminated by ';'
                # Stopping symbols: 'NAME', '}', ';' or 'END' KEYWORD
                self.error(self.NO_MONITOR_SEMICOLON,
                           [self.scanner.KEYWORD,
                            self.scanner.SEMICOLON,
                            self.scanner.NAME,
                            self.scanner.RIGHT_CURLY],
                           [self.scanner.END_ID])
        else:
            # Error: Valid string name required
            # Stopping symbols: 'NAME', '}', ';' or 'END' KEYWORD
            self.error(self.NAME_STRING,
                       [self.scanner.KEYWORD,
                        self.scanner.SEMICOLON,
                        self.scanner.NAME,
                        self.scanner.RIGHT_CURLY],
                       [self.scanner.END_ID])

        # Check for Monitor Semantic errors
        if self.error_count == 0:
            # Only check for semantic errors if no errors so far
            err = self.monitors.make_monitor(device_id, output_id)
            if err != self.monitors.NO_ERROR:
                # Stopping symbols: 'NAME', '}', ';' or 'END' KEYWORD
                self.error(err, [self.scanner.KEYWORD, self.scanner.SEMICOLON,
                                 self.scanner.NAME, self.scanner.RIGHT_CURLY],
                           [self.scanner.END_ID])
