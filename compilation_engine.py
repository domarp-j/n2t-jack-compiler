"""
CompilationEngine
"""


XML_SPACING = 2


class CompilationEngine:
  def __init__(self, tokenizer, vm_writer):
    self.tokenizer = tokenizer
    self.vm_writer = vm_writer
    self.depth = 0


  def run(self):
    self.tokenizer.advance()
    return self.compile_class()


  ###################################################
  # ASSERTIONS
  ###################################################


  def assert_identifier(self):
    assert self.tokenizer.identifier(), f"Expected an identifier but found: {self.tokenizer.current_token}"


  def assert_keyword(self):
    assert self.tokenizer.keyword(), f"Expected a keyword but found: {self.tokenizer.current_token}"


  def assert_return_type(self):
    assert self.tokenizer.keyword() or self.tokenizer.identifier(), f"Expected a keyword or identifier as the return type but found: {self.tokenizer.current_token}"


  def assert_symbol(self, symbol = None):
    if symbol:
      assert self.tokenizer.current_token == symbol, f"Expected {symbol} but found: {self.tokenizer.current_token}"
    else:
      assert self.tokenizer.symbol(), f"Expected a symbol but found: {self.tokenizer.current_token}"


  ###################################################
  # MISCELLANEOUS
  ###################################################


  def add_to_xml(self, tag):
    spacing = " " * XML_SPACING * self.depth

    return f"\n{spacing}{tag}"


  def add_xml_for_current_token(self):
    spacing = " " * XML_SPACING * self.depth

    return f"\n{spacing}{self.tokenizer.current_token_xml()}"


  ###################################################
  # COMPILER METHODS
  ###################################################


  def compile_class(self):
    class_body = "<class>"

    self.depth += 1

    # Add class keyword to XML.
    class_body += self.add_xml_for_current_token()

    # Add class name to XML.
    self.tokenizer.advance()
    self.assert_identifier()
    class_body += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('{')
    class_body += self.add_xml_for_current_token()

    self.tokenizer.advance()

    # Add any class variable declarations to the XML.
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['field', 'static']:
      class_body += self.compile_class_var_dec()
      self.tokenizer.advance()

    # Add any class subroutines to the XML.
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['constructor', 'function', 'method']:
      class_body += self.compile_subroutine_dec()
      self.tokenizer.advance()

    self.assert_symbol('}')
    class_body += self.add_xml_for_current_token()

    self.depth -= 1
    assert self.depth == 0

    class_body += "\n</class>\n"

    return class_body


  def compile_class_var_dec(self):
    class_var_dec = self.add_to_xml("<classVarDec>")

    self.depth += 1

    # Add class variable declarations to XML.
    while self.tokenizer.current_token != ';':
      class_var_dec += self.add_xml_for_current_token()

      self.tokenizer.advance()

    class_var_dec += self.add_xml_for_current_token()

    self.depth -= 1

    class_var_dec += self.add_to_xml("</classVarDec>")

    return class_var_dec


  def compile_do(self):
    do_statement = self.add_to_xml("<doStatement>")

    self.depth += 1

    # Add do keyword to XML.
    do_statement += self.add_xml_for_current_token()

    # Add subroutine call to XML.
    self.tokenizer.advance()
    do_statement += self.compile_subroutine_call()

    self.tokenizer.advance()
    self.assert_symbol(';')
    do_statement += self.add_xml_for_current_token()

    self.depth -= 1

    do_statement += self.add_to_xml("</doStatement>")

    return do_statement


  def compile_expression(self):
    expression = self.add_to_xml("<expression>")

    self.depth += 1

    expression += self.compile_term()

    self.tokenizer.advance()

    if self.tokenizer.op():
      expression += self.add_xml_for_current_token()

      self.tokenizer.advance()
      expression += self.compile_term()

      self.tokenizer.advance()

    self.depth -= 1

    expression += self.add_to_xml("</expression>")

    return expression


  def compile_expression_list(self):
    expression_list = self.add_to_xml("<expressionList>")

    self.depth += 1

    while self.tokenizer.current_token not in [')', '}']:
      if self.tokenizer.current_token == ',':
        expression_list += self.add_xml_for_current_token()
        self.tokenizer.advance()
      else:
        expression_list += self.compile_expression()

    self.depth -= 1

    expression_list += self.add_to_xml("</expressionList>")

    return expression_list


  def compile_if_statement(self):
    if_statement = self.add_to_xml("<ifStatement>")

    self.depth += 1

    # Add if keyword to XML.
    if_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('(')
    if_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    if_statement += self.compile_expression()

    self.assert_symbol(')')
    if_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('{')
    if_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    if_statement += self.compile_statements()

    self.assert_symbol('}')
    if_statement += self.add_xml_for_current_token()

    if self.tokenizer.peek() == 'else':
      self.tokenizer.advance()
      if_statement += self.add_xml_for_current_token()

      self.tokenizer.advance()
      self.assert_symbol('{')
      if_statement += self.add_xml_for_current_token()

      self.tokenizer.advance()
      if_statement += self.compile_statements()

      self.assert_symbol('}')
      if_statement += self.add_xml_for_current_token()

    self.depth -= 1

    if_statement += self.add_to_xml("</ifStatement>")

    return if_statement


  def compile_let(self):
    let_statement = self.add_to_xml("<letStatement>")

    self.depth += 1

    # Add let keyword to XML.
    let_statement += self.add_xml_for_current_token()

    # Add variable to XML.
    self.tokenizer.advance()
    self.assert_identifier()
    let_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol()

    if self.tokenizer.current_token == '[':
      let_statement += self.add_xml_for_current_token()

      self.tokenizer.advance()
      let_statement += self.compile_expression()

      self.assert_symbol(']')
      let_statement += self.add_xml_for_current_token()

      self.tokenizer.advance()

    self.assert_symbol('=')
    let_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    let_statement += self.compile_expression()

    self.assert_symbol(';')
    let_statement += self.add_xml_for_current_token()

    self.depth -= 1

    let_statement += self.add_to_xml("</letStatement>")

    return let_statement


  def compile_parameter_list(self):
    parameter_list = self.add_to_xml("<parameterList>")

    while self.tokenizer.current_token != ')':
      parameter_list += self.add_xml_for_current_token()
      self.tokenizer.advance()

    parameter_list += self.add_to_xml("</parameterList>")

    return parameter_list


  def compile_return(self):
    return_statement = self.add_to_xml("<returnStatement>")

    self.depth += 1

    # Add return keyword to XML.
    return_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()

    if self.tokenizer.current_token != ';':
      return_statement += self.compile_expression()

    self.assert_symbol(';')
    return_statement += self.add_xml_for_current_token()

    self.depth -= 1

    return_statement += self.add_to_xml("</returnStatement>")

    return return_statement


  def compile_statement(self):
    if self.tokenizer.current_token == 'do':
      return self.compile_do()

    if self.tokenizer.current_token == 'let':
      return self.compile_let()

    if self.tokenizer.current_token == 'if':
      return self.compile_if_statement()

    if self.tokenizer.current_token == 'while':
      return self.compile_while_statement()

    if self.tokenizer.current_token == 'return':
      return self.compile_return()

    raise AssertionError(f"Unrecognized token in compile_statement(): {self.tokenizer.current_token}")


  def compile_statements(self):
    statements = self.add_to_xml("<statements>")

    self.depth += 1

    while self.tokenizer.current_token != '}':
      if self.tokenizer.symbol():
        statements += self.add_xml_for_current_token()
      else:
        statements += self.compile_statement()

      self.tokenizer.advance()

    self.depth -= 1

    statements += self.add_to_xml("</statements>")

    return statements


  def compile_subroutine_body(self):
    subroutine_body = self.add_to_xml("<subroutineBody>")

    self.depth += 1

    self.tokenizer.advance()
    self.assert_symbol('{')
    subroutine_body += self.add_xml_for_current_token()

    self.tokenizer.advance()

    while self.tokenizer.current_token == 'var':
      subroutine_body += self.compile_var_dec()
      self.tokenizer.advance()

    subroutine_body += self.compile_statements()

    self.assert_symbol('}')
    subroutine_body += self.add_xml_for_current_token()

    self.depth -= 1

    subroutine_body += self.add_to_xml("</subroutineBody>")

    return subroutine_body


  def compile_subroutine_call(self):
    subroutine_call = ""

    self.assert_identifier()
    subroutine_call += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol()

    if self.tokenizer.current_token == '.':
      subroutine_call += self.add_xml_for_current_token()

      self.tokenizer.advance()
      self.assert_identifier()
      subroutine_call += self.add_xml_for_current_token()

      self.tokenizer.advance()

    self.assert_symbol('(')
    subroutine_call += self.add_xml_for_current_token()

    self.tokenizer.advance()
    subroutine_call += self.compile_expression_list()

    self.assert_symbol(')')
    subroutine_call += self.add_xml_for_current_token()

    return subroutine_call


  def compile_subroutine_dec(self):
    subroutine_dec = self.add_to_xml("<subroutineDec>")

    self.depth += 1

    # Insert the subroutine type (constructor vs. function vs. method).
    self.assert_keyword()
    subroutine_dec += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_return_type()
    subroutine_dec += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_identifier()
    subroutine_dec += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('(')
    subroutine_dec += self.add_xml_for_current_token()

    self.tokenizer.advance()
    subroutine_dec += self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')
    subroutine_dec += self.add_xml_for_current_token()

    subroutine_dec += self.compile_subroutine_body()

    self.depth -= 1

    subroutine_dec += self.add_to_xml("</subroutineDec>")

    return subroutine_dec


  def compile_term(self):
    term = self.add_to_xml("<term>")

    self.depth += 1

    if self.tokenizer.identifier() and self.tokenizer.peek() in ['.', '(', '[']:
      next_token = self.tokenizer.peek()

      # Handle identifiers that precede subroutine calls x().
      if next_token in ['.', '(']:
        term += self.compile_subroutine_call()

      # Handle identifiers that precede array accessors x[].
      elif next_token == '[':
        # Add identifier to XML.
        term += self.add_xml_for_current_token()

        self.tokenizer.advance()
        self.assert_symbol('[')
        term += self.add_xml_for_current_token()

        self.tokenizer.advance()
        term += self.compile_expression()

        self.assert_symbol(']')
        term += self.add_xml_for_current_token()

    # Handle unary operations.
    elif self.tokenizer.unary_op():
      # Add unar operator symbol to XML.
      term += self.add_xml_for_current_token()

      self.tokenizer.advance()
      term += self.compile_term()

    # Handle parentheses surrounding expressions.
    elif self.tokenizer.current_token == '(':
      term += self.add_xml_for_current_token()

      self.tokenizer.advance()
      term += self.compile_expression()

      self.assert_symbol(')')
      term += self.add_xml_for_current_token()

    # Handle:
    # - strings
    # - integers
    # - keywords
    # - identifiers that are not function calls x() or array accessors x[]
    else:
      term += self.add_xml_for_current_token()

    self.depth -= 1

    term += self.add_to_xml("</term>")

    return term


  def compile_var_dec(self):
    var_dec = self.add_to_xml("<varDec>")

    self.depth += 1

    while self.tokenizer.current_token != ';':
      var_dec += self.add_xml_for_current_token()
      self.tokenizer.advance()

    var_dec += self.add_xml_for_current_token()

    self.depth -= 1

    var_dec += self.add_to_xml("</varDec>")

    return var_dec


  def compile_while_statement(self):
    while_statement = self.add_to_xml("<whileStatement>")

    self.depth += 1

    # Add while keyword to XML.
    while_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('(')
    while_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    while_statement += self.compile_expression()

    self.assert_symbol(')')
    while_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    self.assert_symbol('{')
    while_statement += self.add_xml_for_current_token()

    self.tokenizer.advance()
    while_statement += self.compile_statements()

    self.assert_symbol('}')
    while_statement += self.add_xml_for_current_token()

    self.depth -= 1

    while_statement += self.add_to_xml("</whileStatement>")

    return while_statement


