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

class JackTokenizer:
  def __init__(self, input_file):
    # Open input .jack files and tokenize
    pass

  def has_more_tokens(self):
    # Are there more tokens? True or False.
    pass

  def advance(self):
    # Get next token from input, make it current token
    # Should be called iff has_more_tokens() is True
    pass

  def token_type(self):
    # returns one of KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
    pass

  def keyword(self):
    # returns keyword (which is the current constant) as a constant
    # one of CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC, FIELD, LET, DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS
    pass

  def symbol(self):
    # return character which is the current token
    pass

  def identifier(self):
    # return identifier which is current token
    pass

  def int_val(self):
    # return integer value of the current token
    pass

  def string_val(self):
    # return string value of the current token, without dobule quotes
    pass
