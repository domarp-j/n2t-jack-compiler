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
from compilation_engine import CompilationEngine


class JackAnalyzer:
  def __init__(self, jack_input_file):
    self.jack_input_file = jack_input_file

    self.jack_input = ""
    self.xml_output = ""

    with open(jack_input_file) as file:
      for line in file.readlines():
        self.jack_input += self.strip_comment_from_line(line)

    self.strip_newlines()
    self.strip_multiline_comments()

    self.build_tokenizer()
    self.build_xml_output()
    self.write_xml()


  # Remove comments from a given line of Jack code.
  def strip_comment_from_line(self, line):
    # Strip everything after //
    line = re.sub(r"//(.*)", "", line)

    # Strip everything between /* */ and /** */
    return re.sub(r"/\*\*?(.*)\*/", "", line)


  # Remove multiline comments.
  def strip_multiline_comments(self):
    self.jack_input = re.sub(r"/\*\*?(.*?)\*/", "", self.jack_input)


  def strip_newlines(self):
    self.jack_input = re.sub("\n", "", self.jack_input)


  # Initialize JackTokenizer.
  def build_tokenizer(self):
    self.tokenizer = JackTokenizer(self.jack_input)


  # Build XML output.
  def build_xml_output(self):
    self.xml_output = CompilationEngine(self.tokenizer).xml_output


  # Write the XML output string to a file.
  def write_xml(self):
    xml_file_name = self.jack_input_file.replace(".jack", ".test.xml")

    with open(xml_file_name, 'w') as xml_file:
      xml_file.write(self.xml_output)
