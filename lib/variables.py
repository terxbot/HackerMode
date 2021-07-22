import os
import sys

HACKERMODE_PATH = os.path.abspath(__file__.split("/lib/variables.py")[0])
HACKERMODE_TOOLS_PATH = os.path.join(HACKERMODE_PATH, "tools")
HACKERMODE_BIN_PATH = os.path.join(HACKERMODE_PATH, "bin")

if __name__ == "__main__":
    print(eval(sys.argv[1]))
