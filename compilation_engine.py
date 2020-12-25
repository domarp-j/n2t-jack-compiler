"""
CompilationEngine

Gets input from JackTokenizer and emits to output file

NOTES:
Build everything except expressions first.
Add handling of expressions later.
Expressions are difficult due to terms:
- We need to look ahead to check if a term is a variable, an array entry, or subroutine call.
The subroutine call logic should be handled in compile_term().

Refer to Unit 4.5 for details.
"""


class CompilationEngine:
  def __init__(self, tokenizer):
    self.tokenizer = tokenizer
    self.tokenizer.advance()
    self.xml_output = self.compile_class()


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
      assert self.tokenizer.symbol() == symbol, f"Expected {symbol} but found: {self.tokenizer.current_token}"
    else:
      assert self.tokenizer.symbol(), f"Expected a symbol but found: {self.tokenizer.current_token}"


  ###################################################
  # COMPILER METHODS
  ###################################################


  def compile_class(self):
    class_body = "<class>"
    class_body += "<keyword> class </keyword>"

    self.tokenizer.advance()
    self.assert_identifier()
    class_body += f"<identifier> {self.tokenizer.identifier()} </identifier>"

    self.tokenizer.advance()
    self.assert_symbol('{')
    class_body += "<symbol> { </symbol>"

    self.tokenizer.advance()

    while self.tokenizer.keyword() in ['field', 'static']:
      class_body += self.compile_class_var_dec()
      self.tokenizer.advance()

    while self.tokenizer.keyword() in ['constructor', 'function', 'method']:
      class_body += self.compile_subroutine_dec()
      self.tokenizer.advance()

    self.assert_symbol('}')
    class_body += "<symbol> } </symbol>"

    class_body += "</class>"

    return class_body


  def compile_class_var_dec(self):
    class_var_dec = "<classVarDec>"

    while self.tokenizer.symbol() != ';':
      class_var_dec += f"""
        <{self.tokenizer.token_type}> {self.tokenizer.current_token} </{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    class_var_dec += "<symbol> ; </symbol>"
    class_var_dec += "</classVarDec>"

    return class_var_dec


  def compile_do(self):
    do_statement = "<doStatement>"
    do_statement += "<keyword> do </keyword>"

    self.tokenizer.advance()
    do_statement += self.compile_subroutine_call()

    self.tokenizer.advance()
    self.assert_symbol(';')
    do_statement +="<symbol> ; </symbol>"

    do_statement += "</doStatement>"

    return do_statement


  def compile_expression(self):
    expression = "<expression>"

    expression += self.compile_term()

    self.tokenizer.advance()

    if self.tokenizer.op():
      expression += f"<symbol> {self.tokenizer.op()} </symbol>"

      self.tokenizer.advance()
      expression += self.compile_term()

      self.tokenizer.advance()

    expression += "</expression>"

    return expression


  def compile_expression_list(self):
    expression_list = "<expressionList>"

    while self.tokenizer.symbol() not in [')', '}']:
      if self.tokenizer.symbol() == ',':
        expression_list += "<symbol> , </symbol>"
        self.tokenizer.advance()
      else:
        expression_list += self.compile_expression()

    expression_list += "</expressionList>"

    return expression_list


  def compile_if_statement(self):
    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    expression = self.compile_expression()

    self.assert_symbol(')')

    self.tokenizer.advance()
    self.assert_symbol('{')

    self.tokenizer.advance()
    statements = self.compile_statements()

    self.assert_symbol('}')

    else_content = ""

    if self.tokenizer.peek() == 'else':
      self.tokenizer.advance()

      self.tokenizer.advance()
      self.assert_symbol('{')

      self.tokenizer.advance()
      else_statements = self.compile_statements()

      self.assert_symbol('}')

      else_content = f"""
        <keyword> else </keyword>
        <symbol> {{ </symbol>
        {else_statements}
        <symbol> }} </symbol>
      """

    return f"""
      <ifStatement>
        <keyword> if </keyword>
        <symbol> ( </symbol>
        {expression}
        <symbol> ) </symbol>
        <symbol> {{ </symbol>
        {statements}
        <symbol> }} </symbol>
        {else_content}
      </ifStatement>
    """


  def compile_let(self):
    let_statement = "<letStatement>"
    let_statement += "<keyword> let </keyword>"

    self.tokenizer.advance()
    self.assert_identifier()
    let_statement += f"<identifier> {self.tokenizer.identifier()} </identifier>"

    self.tokenizer.advance()
    self.assert_symbol()

    if self.tokenizer.symbol() == '[':
      let_statement += "<symbol> [ </symbol>"

      self.tokenizer.advance()
      let_statement += self.compile_expression()

      self.assert_symbol(']')
      let_statement += "<symbol> ] </symbol>"

      self.tokenizer.advance()

    self.assert_symbol('=')
    let_statement += "<symbol> = </symbol>"

    self.tokenizer.advance()
    let_statement += self.compile_expression()

    self.assert_symbol(';')
    let_statement += "<symbol> ; </symbol>"

    let_statement += "</letStatement>"

    return let_statement


  def compile_parameter_list(self):
    parameter_list = "<parameterList>"

    while self.tokenizer.current_token != ')':
      parameter_list += f"""
        <{self.tokenizer.token_type}> {self.tokenizer.current_token} </{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    parameter_list += "</parameterList>"

    return parameter_list


  def compile_return(self):
    expression = ""

    self.tokenizer.advance()

    if self.tokenizer.current_token != ';':
      expression = self.compile_expression()

    self.assert_symbol(';')

    return f"""
      <returnStatement>
        <keyword> return </keyword>
        {expression}
        <symbol> ; </symbol>
      </returnStatement>
    """


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
    statements = "<statements>"

    while self.tokenizer.current_token != '}':
      if self.tokenizer.symbol():
        statements += f"<symbol>{self.tokenizer.symbol()}</symbol>"
      else:
        statements += self.compile_statement()

      self.tokenizer.advance()

    statements += "</statements>"

    return statements


  def compile_subroutine_body(self):
    subroutine_body = "<subroutineBody>"

    self.tokenizer.advance()
    self.assert_symbol('{')
    subroutine_body += "<symbol> { </symbol>"

    self.tokenizer.advance()

    while self.tokenizer.keyword() == 'var':
      subroutine_body += self.compile_var_dec()
      self.tokenizer.advance()

    subroutine_body += self.compile_statements()

    self.assert_symbol('}')
    subroutine_body += "<symbol> } </symbol>"

    subroutine_body += "</subroutineBody>"

    return subroutine_body


  def compile_subroutine_call(self):
    subroutine_call = ""

    self.assert_identifier()
    subroutine_call += f"<identifier> {self.tokenizer.identifier()} </identifier>"

    self.tokenizer.advance()
    self.assert_symbol()

    if self.tokenizer.symbol() == '.':
      subroutine_call += "<symbol> . </symbol>"

      self.tokenizer.advance()
      self.assert_identifier()
      subroutine_call += f"<identifier> {self.tokenizer.identifier()} </identifier>"

      self.tokenizer.advance()

    self.assert_symbol('(')
    subroutine_call +="<symbol> ( </symbol>"

    self.tokenizer.advance()
    subroutine_call += self.compile_expression_list()

    self.assert_symbol(')')
    subroutine_call +="<symbol> ) </symbol>"

    return subroutine_call


  def compile_subroutine_dec(self):
    subroutine_dec = "<subroutineDec>"

    # Insert the subroutine type (constructor vs. function vs. method).
    subroutine_dec += f"<keyword>{self.tokenizer.keyword()}</keyword>"

    self.tokenizer.advance()
    self.assert_return_type()
    subroutine_dec += f"<{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>"

    self.tokenizer.advance()
    self.assert_identifier()
    subroutine_dec += f"<identifier>{self.tokenizer.identifier()}</identifier>"

    self.tokenizer.advance()
    self.assert_symbol('(')
    subroutine_dec += "<symbol> ( </symbol>"

    self.tokenizer.advance()
    subroutine_dec += self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')
    subroutine_dec += "<symbol> ) </symbol>"

    subroutine_dec += self.compile_subroutine_body()

    subroutine_dec += "</subroutineDec>"

    return subroutine_dec


  def compile_term(self):
    term = "<term>"

    if self.tokenizer.identifier() and self.tokenizer.peek() in ['.', '(', '[']:
      identifier = self.tokenizer.identifier()
      next_token = self.tokenizer.peek()

      # Handle identifiers that precede subroutine calls x().
      if next_token in ['.', '(']:
        term += self.compile_subroutine_call()

      # Handle identifiers that precede array accessors x[].
      elif next_token == '[':
        term += f"<identifier> {identifier} </identifier>"

        self.tokenizer.advance()
        term += f"<symbol> [ </symbol>"

        self.tokenizer.advance()
        term += self.compile_expression()

        self.assert_symbol(']')
        term += f"<symbol> ] </symbol>"

    # Handle unary operations.
    elif self.tokenizer.unary_op():
      term += f"<symbol> {self.tokenizer.unary_op()} </symbol>"

      self.tokenizer.advance()
      term += self.compile_term()

    # Handle parentheses surrounding expressions.
    elif self.tokenizer.symbol() == '(':
      term += "<symbol> ( </symbol>"

      self.tokenizer.advance()
      term += self.compile_expression()

      self.assert_symbol(')')
      term += "<symbol> ) </symbol>"

    # Handle strings.
    elif self.tokenizer.string_val():
      term += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.string_val()}</{self.tokenizer.token_type}>
      """

    # Handle:
    # - integers
    # - keywords
    # - identifiers that are not function calls x() or array accessors x[]
    else:
      term += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """

    term += "</term>"

    return term


  def compile_var_dec(self):
    var_dec = "<varDec>"

    while self.tokenizer.symbol() != ';':
      var_dec += f"""
        <{self.tokenizer.token_type}> {self.tokenizer.current_token} </{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    var_dec += "<symbol> ; </symbol>"
    var_dec += "</varDec>"

    return var_dec


  def compile_while_statement(self):
    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    expression = self.compile_expression()

    self.assert_symbol(')')

    self.tokenizer.advance()
    self.assert_symbol('{')

    self.tokenizer.advance()
    statements = self.compile_statements()

    self.assert_symbol('}')

    return f"""
      <whileStatement>
        <keyword> while </keyword>
        <symbol> ( </symbol>
        {expression}
        <symbol> ) </symbol>
        <symbol> {{ </symbol>
        {statements}
        <symbol> }} </symbol>
      </whileStatement>
    """

