#######################################
# MAIN
#######################################

"""
EXPECTED COMMAND:
JackAnalyzer input

input - fileName.jack or directory of .jack files
output - fileName.xml or directory of .jack and .xml files

THREE MODULES:
JackAnalyzer
JackTokenizer
CompilationEngine

JackAnalyzer should use JackTokenizer
Lexical elements -> JackTokenizer
All other grammer elements -> CompilationEngine
CompilationEngine should also use JackTokenizer

STEPS:
Build JackTokenizer
Build CompilationEngine
"""


import sys
import os

from jack_analyzer import JackAnalyzer


def main():
  jack_input_file = sys.argv[1]

  # if os.path.isdir(vm_input):
  #   # Create an ASM file within the directory.
  #   asm_file_name = create_asm_for_dir(vm_input)

  #   # Parse each VM file and write to ASM file.
  #   write_asm_from_dir(vm_input, asm_file_name)
  # elif os.path.isfile(vm_input):
  #   # Parse the VM file.
  #   asm_instructions = parse_vm(vm_input)
  #   # Write the ASM file.
  #   write_asm(asm_instructions, vm_input)
  # else:
  #   print('Input is not a file or directory. Please try again.')

  JackAnalyzer(jack_input_file)


if __name__ == "__main__":
  main()
