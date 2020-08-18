"""__init__ file to create package, also creates some
package wide global variables
"""
import os
import sys

BOARD_LOC = os.path.join(sys.path[0], __name__, "boards")
