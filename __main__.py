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

def main():
  pass

if __name__ == "__main__":
  main()
