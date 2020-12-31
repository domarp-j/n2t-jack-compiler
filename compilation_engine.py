"""
CompilationEngine
"""


from symbol_table import SymbolTable


class CompilationEngine:
  def __init__(self, tokenizer, vm_writer):
    self.tokenizer = tokenizer
    self.vm_writer = vm_writer

    self.class_symbol_table = SymbolTable()
    self.subroutine_symbol_table = SymbolTable()


  def run(self):
    self.tokenizer.advance()
    return self.compile_class()


  ###################################################
  # ASSERTIONS
  ###################################################


  def assert_identifier(self):
    assert self.tokenizer.identifier(), f"Expected an identifier but found: {self.tokenizer.current_token}"


  def assert_keyword(self, keyword = None):
    if keyword and type(keyword) is list:
      assert self.tokenizer.keyword() and self.tokenizer.current_token in keyword, f"Expected one of keywords {keyword} but found: {self.tokenizer.current_token}"
    elif keyword:
      assert self.tokenizer.keyword() and self.tokenizer.current_token == keyword, f"Expected keyword {keyword} but found: {self.tokenizer.current_token}"
    else:
      assert self.tokenizer.keyword(), f"Expected a keyword but found: {self.tokenizer.current_token}"


  def assert_return_type(self):
    assert self.tokenizer.keyword() or self.tokenizer.identifier(), f"Expected a keyword or identifier as the return type but found: {self.tokenizer.current_token}"


  def assert_symbol(self, symbol = None):
    if symbol and type(symbol) is list:
      assert self.tokenizer.symbol() and self.tokenizer.current_token in symbol, f"Expected one of symbols {symbol} but found: {self.tokenizer.current_token}"
    elif symbol:
      assert self.tokenizer.symbol() and self.tokenizer.current_token == symbol, f"Expected symbol \"{symbol}\" but found: {self.tokenizer.current_token}"
    else:
      assert self.tokenizer.symbol(), f"Expected a symbol but found: {self.tokenizer.current_token}"



  ###################################################
  # COMPILER METHODS
  ###################################################


  def compile_class(self):
    self.assert_keyword('class')

    # Class Name
    self.tokenizer.advance()
    self.assert_identifier()

    self.tokenizer.advance()
    self.assert_symbol('{')

    # Class Variables (field, static)
    self.tokenizer.advance()
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['field', 'static']:
      self.class_symbol_table.reset()
      self.compile_class_var_dec()
      self.tokenizer.advance()

    # Subroutines
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['constructor', 'function', 'method']:
      self.subroutine_symbol_table.reset()
      self.compile_subroutine_dec()
      self.tokenizer.advance()

    self.assert_symbol('}')


  def compile_class_var_dec(self):
    kind = self.tokenizer.current_token
    self.tokenizer.advance()

    typ = self.tokenizer.current_token
    self.tokenizer.advance()

    name = self.tokenizer.current_token
    self.tokenizer.advance()

    self.class_symbol_table.define(name, typ, kind)

    while self.tokenizer.current_token != ';':
      self.assert_symbol(',')
      self.tokenizer.advance()

      name = self.tokenizer.current_token
      self.tokenizer.advance()

      self.class_symbol_table.define(name, typ, kind)


  def compile_do(self):
    self.assert_keyword('do')

    self.tokenizer.advance()
    self.compile_subroutine_call()

    self.tokenizer.advance()
    self.assert_symbol(';')


  def compile_expression(self):
    self.compile_term()

    self.tokenizer.advance()

    if self.tokenizer.op():
      # TODO: Handle op.

      self.tokenizer.advance()
      self.compile_term()

      self.tokenizer.advance()


  def compile_expression_list(self):
    while self.tokenizer.current_token not in [')', '}']:
      if self.tokenizer.current_token == ',':
        self.tokenizer.advance()
      else:
        self.compile_expression()


  # def compile_if_statement(self):
  #   if_statement = self.add_to_xml("<ifStatement>")

  #   self.depth += 1

  #   # Add if keyword to XML.
  #   if_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   self.assert_symbol('(')
  #   if_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   if_statement += self.compile_expression()

  #   self.assert_symbol(')')
  #   if_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   self.assert_symbol('{')
  #   if_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   if_statement += self.compile_statements()

  #   self.assert_symbol('}')
  #   if_statement += self.add_xml_for_current_token()

  #   if self.tokenizer.peek() == 'else':
  #     self.tokenizer.advance()
  #     if_statement += self.add_xml_for_current_token()

  #     self.tokenizer.advance()
  #     self.assert_symbol('{')
  #     if_statement += self.add_xml_for_current_token()

  #     self.tokenizer.advance()
  #     if_statement += self.compile_statements()

  #     self.assert_symbol('}')
  #     if_statement += self.add_xml_for_current_token()

  #   self.depth -= 1

  #   if_statement += self.add_to_xml("</ifStatement>")

  #   return if_statement


  # def compile_let(self):
  #   let_statement = self.add_to_xml("<letStatement>")

  #   self.depth += 1

  #   # Add let keyword to XML.
  #   let_statement += self.add_xml_for_current_token()

  #   # Add variable to XML.
  #   self.tokenizer.advance()
  #   self.assert_identifier()
  #   let_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   self.assert_symbol()

  #   if self.tokenizer.current_token == '[':
  #     let_statement += self.add_xml_for_current_token()

  #     self.tokenizer.advance()
  #     let_statement += self.compile_expression()

  #     self.assert_symbol(']')
  #     let_statement += self.add_xml_for_current_token()

  #     self.tokenizer.advance()

  #   self.assert_symbol('=')
  #   let_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   let_statement += self.compile_expression()

  #   self.assert_symbol(';')
  #   let_statement += self.add_xml_for_current_token()

  #   self.depth -= 1

  #   let_statement += self.add_to_xml("</letStatement>")

  #   return let_statement


  def compile_parameter_list(self):
    param_content = []

    while self.tokenizer.current_token != ')':
      if self.tokenizer.current_token != ',':
        param_content.append(self.tokenizer.current_token)

      self.tokenizer.advance()

    typ = None

    while len(param_content) > 0:
      val = param_content.pop(0)

      if typ == None:
        typ = val
      else:
        name = val
        self.subroutine_symbol_table.define(name, typ, 'argument')
        typ = None


  def compile_return(self):
    self.assert_keyword('return')

    self.tokenizer.advance()

    if self.tokenizer.current_token != ';':
      self.compile_expression()

    self.assert_symbol(';')


  def compile_statement(self):
    if self.tokenizer.current_token == 'do':
      return self.compile_do()

    # if self.tokenizer.current_token == 'let':
    #   return self.compile_let()

    # if self.tokenizer.current_token == 'if':
    #   return self.compile_if_statement()

    # if self.tokenizer.current_token == 'while':
    #   return self.compile_while_statement()

    if self.tokenizer.current_token == 'return':
      return self.compile_return()

    raise AssertionError(f"Unrecognized token in compile_statement(): {self.tokenizer.current_token}")


  def compile_statements(self):
    while self.tokenizer.current_token != '}':
      if self.tokenizer.symbol():
        pass
      else:
        self.compile_statement()

      self.tokenizer.advance()


  def compile_subroutine_body(self):
    self.tokenizer.advance()
    self.assert_symbol('{')

    self.tokenizer.advance()
    while self.tokenizer.current_token == 'var':
      self.compile_var_dec()
      self.tokenizer.advance()

    self.compile_statements()

    self.assert_symbol('}')


  def compile_subroutine_call(self):
    # Subroutine name OR class name
    self.assert_identifier()

    self.tokenizer.advance()
    self.assert_symbol(['(', '.'])

    # If current token is period, this is a method call, e.g. obj.doThing().
    if self.tokenizer.current_token == '.':
      # Method name, e.g. doAThing
      self.tokenizer.advance()
      self.assert_identifier()

      self.tokenizer.advance()

    self.assert_symbol('(')

    self.tokenizer.advance()
    self.compile_expression_list()

    self.assert_symbol(')')


  def compile_subroutine_dec(self):
    self.assert_keyword(['constructor', 'method', 'function'])
    subroutine_type = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_return_type()
    return_type = self.tokenizer.current_token

    if subroutine_type == 'method':
      self.subroutine_symbol_table.define('this', return_type, 'argument')

    # Subroutine name
    self.tokenizer.advance()
    self.assert_identifier()

    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')

    self.compile_subroutine_body()


  def compile_term(self):
    if self.tokenizer.identifier() and self.tokenizer.peek() in ['.', '(', '[']:
      next_token = self.tokenizer.peek()

      # Handle identifiers that precede subroutine calls x().
      if next_token in ['.', '(']:
        self.compile_subroutine_call()

      # Handle identifiers that precede array accessors x[].
      elif next_token == '[':
        # TODO: Handle identifier.

        self.tokenizer.advance()
        self.assert_symbol('[')

        self.tokenizer.advance()
        self.compile_expression()

        self.assert_symbol(']')

    # Handle unary operations.
    elif self.tokenizer.unary_op():
      # TODO: Handle unary op.

      self.tokenizer.advance()
      self.compile_term()

    # Handle parentheses surrounding expressions.
    elif self.tokenizer.current_token == '(':
      self.tokenizer.advance()
      self.compile_expression()

      self.assert_symbol(')')

    # Handle:
    # - strings
    # - integers
    # - keywords
    # - identifiers that are not function calls x() or array accessors x[]
    else:
      # TODO: Handle these
      pass


  def compile_var_dec(self):
    self.assert_keyword('var')
    kind = 'local'
    self.tokenizer.advance()

    typ = self.tokenizer.current_token
    self.tokenizer.advance()

    name = self.tokenizer.current_token
    self.tokenizer.advance()

    self.subroutine_symbol_table.define(name, typ, kind)

    while self.tokenizer.current_token != ';':
      self.assert_symbol(',')
      self.tokenizer.advance()

      name = self.tokenizer.current_token
      self.tokenizer.advance()

      self.subroutine_symbol_table.define(name, typ, kind)


  # def compile_while_statement(self):
  #   while_statement = self.add_to_xml("<whileStatement>")

  #   self.depth += 1

  #   # Add while keyword to XML.
  #   while_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   self.assert_symbol('(')
  #   while_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   while_statement += self.compile_expression()

  #   self.assert_symbol(')')
  #   while_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   self.assert_symbol('{')
  #   while_statement += self.add_xml_for_current_token()

  #   self.tokenizer.advance()
  #   while_statement += self.compile_statements()

  #   self.assert_symbol('}')
  #   while_statement += self.add_xml_for_current_token()

  #   self.depth -= 1

  #   while_statement += self.add_to_xml("</whileStatement>")

  #   return while_statement


