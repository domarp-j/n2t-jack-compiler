#######################################
# MAIN
#######################################

"""
EXPECTED COMMAND:
JackCompiler input

input - fileName.jack or directory of .jack files
output - fileName.vm or directory of .jack and .vm files
"""


import sys

from jack_compiler import JackCompiler


def main():
  jack_input = sys.argv[1]

  JackCompiler(jack_input)


if __name__ == "__main__":
  main()
