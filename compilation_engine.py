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


import pdb


class CompilationEngine:
  def __init__(self, tokenizer):
    self.tokenizer = tokenizer
    self.tokenizer.advance()
    self.xml_output = self.compile_class()


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


  def compile_subroutine_dec(self):
    subroutine_type = self.tokenizer.keyword()

    self.tokenizer.advance()
    self.assert_keyword()
    return_type = self.tokenizer.keyword()

    self.tokenizer.advance()
    self.assert_identifier()
    identifier = self.tokenizer.identifier()

    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    parameter_list = self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')

    return f"""
      <subroutineDec>
        <keyword> {subroutine_type} </keyword>
        <keyword> {return_type} </keyword>
        <identifier> {identifier} </identifier>
        <symbol> ( </symbol>
        {parameter_list}
        <symbol> ) </symbol>
        {self.compile_subroutine_body()}
      </subroutineDec>
    """


  def compile_parameter_list(self):
    parameter_list = "<parameterList>"

    while self.tokenizer.current_token != ')':
      parameter_list += f"""
        <{self.tokenizer.token_type}> {self.tokenizer.current_token} </{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    parameter_list += "</parameterList>"

    return parameter_list


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
        <keyword> if </keyword>
        <symbol> ( </symbol>
        {expression}
        <symbol> ) </symbol>
        <symbol> {{ </symbol>
        {statements}
        <symbol> }} </symbol>
      </whileStatement>
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


  def compile_do(self):
    do_statement = "<doStatement>"
    do_statement += "<keyword> do </keyword>"

    self.tokenizer.advance()
    self.assert_identifier()
    do_statement += f"<identifier> {self.tokenizer.identifier()} </identifier>"

    self.tokenizer.advance()
    self.assert_symbol()

    if self.tokenizer.symbol() == '.':
      do_statement += "<symbol> . </symbol>"

      self.tokenizer.advance()
      self.assert_identifier()
      do_statement += f"<identifier> {self.tokenizer.identifier()} </identifier>"

    self.tokenizer.advance()
    self.assert_symbol('(')
    do_statement +="<symbol> ( </symbol>"

    self.tokenizer.advance()
    do_statement += self.compile_expression_list()

    while self.tokenizer.symbol() != ';':
      self.assert_symbol()
      do_statement += f"<symbol> {self.tokenizer.symbol()} </symbol>"
      self.tokenizer.advance()

    do_statement +="<symbol> ; </symbol>"

    do_statement += "</doStatement>"

    return do_statement


  def compile_return(self):
    expression = ""

    self.tokenizer.advance()

    if self.tokenizer.current_token != ';':
      expression = self.compile_expression()
      self.tokenizer.advance()

    self.assert_symbol(';')

    return f"""
      <returnStatement>
        <keyword> return </keyword>
        {expression}
        <symbol> ; </symbol>
      </returnStatement>
    """


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


  def compile_term(self):
    token_type = self.tokenizer.token_type
    current_token = self.tokenizer.current_token

    return f"""
      <term>
        <{token_type}> {current_token} </{token_type}>
      </term>
    """


  def compile_expression_list(self):
    expression_list = "<expressionList>"

    while self.tokenizer.symbol() in (None, ','):
      if self.tokenizer.symbol() == ',':
        expression_list += "<symbol> , </symbol>"
      else:
        expression_list += self.compile_expression()

      self.tokenizer.advance()

    expression_list += "</expressionList>"

    return expression_list


  def assert_identifier(self):
    assert self.tokenizer.identifier(), f"Expected an identifier but found: {self.tokenizer.current_token}"


  def assert_keyword(self):
    assert self.tokenizer.keyword(), f"Expected a keyword but found: {self.tokenizer.current_token}"


  def assert_symbol(self, symbol = None):
    if symbol:
      assert self.tokenizer.symbol() == symbol, f"Expected {symbol} but found: {self.tokenizer.current_token}"
    else:
      assert self.tokenizer.symbol(), f"Expected a symbol but found: {self.tokenizer.current_token}"

