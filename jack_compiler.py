"""
JackCompiler

Given the path for a single .jack file or directory of .jack files:
- Create a JackTokenizer for each .jack file
- Use SymbolTable, CompilationEngine, and VMWriter to write the VM code into the output .vm file
"""


import os
import re

from jack_tokenizer import JackTokenizer
from vm_writer import VMWriter
from compilation_engine import CompilationEngine


class JackCompiler:
  def __init__(self, argv1):
    self.jack_files = self.handle_file_vs_dir(argv1)

    for jack_file in self.jack_files:
      self.jack_input = ""
      self.xml_output = ""

      with open(jack_file) as file:
        for line in file.readlines():
          self.jack_input += self.strip_comment_from_line(line)

      self.strip_newlines()
      self.strip_multiline_comments()

      # Add the following code to test the tokenizer.
      # self.build_tokenizer()
      # self.test_tokenizer(jack_file)

      self.build_tokenizer()
      self.build_vm_writer(jack_file)

      self.run_compilation_engine()

      self.vm_writer.close()


  # Given a Jack file name or a directory of Jack files,
  # return an array of Jack file names.
  def handle_file_vs_dir(self, argv1):
    if os.path.isdir(argv1):
      return [
        f"{argv1}/{file}"
        for file in os.listdir(argv1)
        if len(file) > 5 and file[-5:] == '.jack'
      ]
    else:
      return [argv1]


  # Remove comments from a given line of Jack code.
  def strip_comment_from_line(self, line):
    # Strip everything after //
    line = re.sub(r"//(.*)", "", line)

    # Strip everything between /* */ and /** */
    return re.sub(r"/\*\*?(.*)\*/", "", line)


  # Remove multiline comments.
  def strip_multiline_comments(self):
    self.jack_input = re.sub(r"/\*\*?(.*?)\*/", "", self.jack_input)


  # Remove newlines.
  def strip_newlines(self):
    self.jack_input = re.sub("\n", "", self.jack_input)


  # Initialize the JackTokenizer.
  def build_tokenizer(self):
    self.tokenizer = JackTokenizer(self.jack_input)


  # Initialize the JackTokenizer.
  def build_vm_writer(self, jack_file):
    self.vm_writer = VMWriter(jack_file)


  # Run the CompilationEngine.
  def run_compilation_engine(self):
    CompilationEngine(self.tokenizer, self.vm_writer).run()


  # Create an XML file to test the tokenizer.
  def test_tokenizer(self, jack_file):
    token_xml_file_name = jack_file.replace(".jack", "T.xml")

    with open(token_xml_file_name, 'w') as xml_file:
      xml_file.write(self.tokenizer.run_test())





