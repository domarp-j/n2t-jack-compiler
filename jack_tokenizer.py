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


# TOKEN TYPES
KEYWORD = 'keyword'
SYMBOL = 'symbol'
IDENTIFIER = 'identifier'
INT_CONST = 'integerConstant'
STRING_CONST = 'stringConstant'


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
  'return',
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

    # Store the token type.
    self.token_type = None

    # Store in state whether the tokenizer is currently in a string.
    self.string_mode = False


  # Determine whether tokenization is complete.
  def has_more_tokens(self):
    return self.token_pos < len(self.input_stream)


  # Advance to the next token.
  def advance(self, reset = True):
    if not self.has_more_tokens():
      return

    if reset:
      self.current_token = ""

    current_char = self.input_stream[self.token_pos]
    self.token_pos += 1

    # Handle quotations, which indicate strings.
    # Note that it could be an opening or closing quotation.
    if current_char == '"':
      self.current_token += '"'

      if self.string_mode:
        self.string_mode = False
      else:
        self.string_mode = True
        self.advance(reset = False)

    # Handle alphanumeric characters and underscores.
    if re.search(r"\w", current_char) or self.string_mode:
      self.current_token += current_char
      self.advance(reset = False)

    # Handle symbols.
    if current_char in SYMBOLS:
      if self.current_token:
        self.token_pos -= 1
      else:
        self.current_token = current_char

    # Advance further if current token is empty.
    if not self.current_token:
      self.advance()

    self.determine_token_type()


  # Determine the current token's type.
  # See TOKEN TYPES at the top of the file for a full list.
  def determine_token_type(self):
    if self.current_token == "":
      self.token_type = None
    elif self.current_token in SYMBOLS:
      self.token_type = SYMBOL
    elif self.current_token in KEYWORDS:
      self.token_type = KEYWORD
    elif re.search(r"\D", self.current_token) == None:
      self.token_type = INT_CONST
    elif self.current_token[0] == '"':
      self.token_type = STRING_CONST
    else:
      self.token_type = IDENTIFIER


  # Return the current token as a keyword.
  # See KEYWORDS for a full list.
  def keyword(self):
    if self.token_type != KEYWORD:
      return

    return self.current_token


  # Return the current token as a symbol.
  def symbol(self):
    if self.token_type != SYMBOL:
      return

    return self.current_token


  # Return the current token (an identifier).
  def identifier(self):
    if self.token_type != IDENTIFIER:
      return

    return self.current_token


   # Return the integer value of the current token.
  def int_val(self):
    if self.token_type != INT_CONST:
      return

    return int(self.current_token)


  # Return the string value of the current token, without double quotes or newlines.
  def string_val(self):
    if self.token_type != STRING_CONST:
      return

    return re.sub(r"\"|\n", "", self.current_token)

