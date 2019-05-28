"""Record the error messages and location.

Used in the Logic Simulator project to record the specified error

Classes
-------
Error - records the particular errors

"""

class Error:
    "DOCSTRING stuff"

    def __init__(self, msg = "", line_num = "", line = "", carat_pos = ""):

        self.msg = msg
        self.line_num = line_num
        self.line = line
        self.carat_pos = carat_pos
