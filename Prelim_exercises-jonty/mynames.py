"""Implements a name table for lexical analysis.

Classes
-------
MyNames - implements a name table for lexical analysis.
"""


class MyNames:

    """Implements a name table for lexical analysis.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    lookup(self, name_string): Returns the corresponding name ID for the
                 given name string. Adds the name if not already present.

    get_string(self, name_id): Returns the corresponding name string for the
                 given name ID. Returns None if the ID is not a valid index.
    """

    def __init__(self):
        """Initialise the names list."""
        self.names = []

    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.

        If the name string is not present in the names list, add it.
        """
        if not isinstance(name_string, str):
            raise TypeError('Name given must be a string')
        for i in range(len(self.names)):
            if self.names[i] == name_string:
                return i
        self.names.append(name_string)
        return len(self.names)-1

    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.

        If the name ID is not a valid index into the names list, return None.
        """
        if isinstance(name_id, str):
            raise TypeError('Name_ID given must be an integer not a string')
        if isinstance(name_id, float):
            raise TypeError('Name_ID given must be an integer not a float')
        if name_id < 0:
            raise ValueError('Name_ID given must be greater than zero')
        if name_id >= len(self.names):
            return None
        else:
            return self.names[name_id]
