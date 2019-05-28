"""Record the error messages and location.

Used in the Logic Simulator project to record an error and assign it attributes
of importance to the GUI.

Classes
-------
Error - holds a record of the error's user message, line number, line and
position.

"""

class Error:
    """Record an error's user message, line number, line and position.

    An error object is initialised with blank parameters but each is
    reassigned in the scanner and/or parser. They can then be recalled
    by the GUI when attempting to display helpful error messages to the user.

    Parameters
    ----------
    msg: descriptive error message highlighting the issue.
    line_num: string "Line x:" where x is the line number of the error.
    line: string of the line on which the error exists.
    caret_pos: string with a caret pointing to the correct character of 'line'.

    Public Methods
    -------------
    No public methods.

    """

    def __init__(self, msg = "", line_num = "", line = "", caret_pos = ""):

        self.msg = msg
        self.line_num = line_num
        self.line = line
        self.caret_pos = caret_pos
