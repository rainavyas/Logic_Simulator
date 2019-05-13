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
        if not type(name_string) is str:
            raise TypeError("name has to be a string")

        if not (name_string in self.names):
            self.names.append(name_string)
        return self.names.index(name_string)

    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.
        If the name ID is not a valid index into the names list, return None.
        """
        if not type(name_id) is int:
            raise TypeError("ID has to be an integer")

        if name_id < 0:
            raise ValueError("ID has to be positive")

        if name_id >= len(self.names):
            return None
        else:
            return self.names[name_id]
