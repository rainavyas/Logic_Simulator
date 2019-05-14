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
        self.name_list = []

    def lookup(self, name_string):
        """Return the corresponding name ID for the given name_string.

        If the name string is not present in the names list, add it.
        """
        if type(name_string) is str:
            if name_string in self.name_list:
                return self.name_list.index(name_string)
            else:
                self.name_list.append(name_string)
                return self.name_list.index(name_string)
        else:
            raise TypeError

    def get_string(self, name_id):
        """Return the corresponding name string for the given name_id.

        If the name ID is not a valid index into the names list, return None.
        """
        if name_id < 0:
            raise ValueError
        elif name_id < len(self.name_list):
            string = self.name_list[name_id]
        else:
            return
        return string
