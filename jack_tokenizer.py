"""
JackTokenizer

Given the compiler's input, advance the input one token at a time.
Ignore white space!
Get the current *value* and *type* of the current token.

NOTES:
Strings should be outputted without double quotes.
< > " and & should output &lt; &gt; &quot; and &amp;

See "Lexical elements" in jack-grammer.png
"""


import re
import pdb


KEYWORD = 'KEYWORD'
SYMBOL = 'SYMBOL'
IDENTIFIER = 'IDENTIFIER'
INT_CONST = 'INT_CONST'
STRING_CONST = 'STRING_CONST'


KEYWORDS = [
  'boolean',
  'char',
  'class',
  'constructor',
  'do',
  'else',
  'false',
  'field',
  'function',
  'if',
  'int',
  'let',
  'method',
  'null',
  'return'
  'static',
  'this',
  'true',
  'var',
  'void',
  'while'
]


SYMBOLS = [
  '{',
  '}',
  '(',
  ')',
  '[',
  ']',
  '.',
  ',',
  ';',
  '+',
  '-',
  '*',
  '/',
  '&',
  '|',
  '<',
  '>',
  '=',
  '~'
]


class JackTokenizer:
  def __init__(self, input_stream):
    # Store input file contents as a string stream.
    self.input_stream = input_stream

    # Store the current token.
    self.current_token = ""

    # Store the position of the next possible token.
    self.token_pos = 0

    # Store in state whether the tokenizer is currently in a string.
    self.string_mode = False


  def has_more_tokens(self):
    # Return True if there are more tokens to parse.
    return self.token_pos < len(self.input_stream)


  def advance(self, reset = True):
    if not self.has_more_tokens():
      return

    if reset:
      self.current_token = ""

    current_char = self.input_stream[self.token_pos]
    self.token_pos += 1

    if re.search(r"\w", current_char):
      self.current_token += current_char
      self.advance(reset = False)

    if current_char in SYMBOLS:
      if self.current_token:
        self.token_pos -= 1
      else:
        self.current_token = current_char

    if not self.current_token:
      self.advance()


  def token_type(self):
    if self.current_token == "":
      return None
    elif self.current_token in SYMBOLS:
      return SYMBOL
    elif self.current_token in KEYWORDS:
      return KEYWORD
    elif re.search(r"\D", self.current_token) == None:
      return INT_CONST
    elif self.current_token[0] == '"':
      return STRING_CONST
    else:
      return IDENTIFIER


  def keyword(self):
    # Returns the current token as a keyword.
    # See KEYWORDS for a full list.
    if self.token_type != KEYWORD:
      pass
    return self.current_token


  def symbol(self):
    # Return the current token as a symbol.
    if self.token_type != SYMBOL:
      pass
    return self.current_token


  def identifier(self):
    # Return the current token (an identifier).
    if self.token_type != IDENTIFIER:
      pass
    return self.current_token


  def int_val(self):
    # Return the integer value of the current token.
    if self.token_type != INT_CONST:
      pass
    return int(self.current_token)


  def string_val(self):
    # Return the string value of the current token, without double quotes or newlines.
    if self.token_type != STRING_CONST:
      pass
    return re.sub(r"\"|\n", "", self.current_token)


  # def token_type_from_chars(self):
  #   # Do nothing if current token is empty.
  #   if self.token_type == None:
  #     return

  #   # Determine the token type from a sequence of alphanumeric characters.
  #   if self.current_token in KEYWORDS:
  #     self.token_type = KEYWORD
  #   elif self.current_token[0] == '"':
  #     self.token_type = STRING_CONST
  #   elif re.search(r"\d", self.token_type[0]) != None:
  #     self.token_type = INT_CONST
  #   else:
  #     self.token_type = IDENTIFIER

