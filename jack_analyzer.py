"""
JackAnalyzer

Top-most module
Given a single .jack file or directory of .jack files:
- Create a JackTokenizer from fileName.jack
- Create an output file called fileName.xml and prepare it for writing
- Create and use CompilationEngine to compile input JackTokenizer into output file
"""


import re

from jack_tokenizer import JackTokenizer


class JackAnalyzer:
  def __init__(self, jack_input_file):
    self.jack_input = ""

    with open(jack_input_file) as file:
      for line in file.readlines():
        self.jack_input += self.strip_comments(line)

    self.tokenize()


  def strip_comments(self, line):
    # Strip everything after //
    line = re.sub(r"//(.*)", "", line)

    # Strip everything between /* */
    return re.sub(r"/\*(.*?)\*/", "", line)


  def tokenize(self):
    token_stream = JackTokenizer(self.jack_input)

    while token_stream.has_more_tokens():
      print(token_stream.current_token)
      print(token_stream.token_type)
      print('~~~~~~~~~~~~~~~~~~~~~~`')
      token_stream.advance()
