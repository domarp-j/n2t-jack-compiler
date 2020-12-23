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
    self.xml_output = self.compile_statement()


  def compile_class(self): # DONE
    self.tokenizer.advance()
    identifier = self.tokenizer.identifier()

    self.tokenizer.advance()
    self.assert_symbol('{')

    class_body = ""

    self.tokenizer.advance()

    while self.tokenizer.symbol() != '}':
      class_body += self.compile_statement()
      self.tokenizer.advance()

    return f"""
      <class>
        <keyword>class</keyword>
        <identifier>{identifier}</identifier>
        <symbol>{{</symbol>
        {class_body}
        <symbol>}}</symbol>
      </class>
    """


  def compile_class_var_dec(self): # DONE
    class_var_dec = "<classVarDec>"

    while self.tokenizer.symbol() != ';':
      class_var_dec += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    class_var_dec += "<symbol>;</symbol>"
    class_var_dec += "</classVarDec>"

    return class_var_dec


  def compile_subroutine_dec(self): # DONE
    subroutine_type = self.tokenizer.keyword()

    self.tokenizer.advance()
    return_type = self.tokenizer.keyword()

    self.tokenizer.advance()
    identifier = self.tokenizer.identifier()

    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    parameter_list = self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')

    return f"""
      <subroutineDec>
        <keyword>{subroutine_type}</keyword>
        <keyword>{return_type}</keyword>
        <identifier>{identifier}</identifier>
        <symbol>(</symbol>
        {parameter_list}
        <symbol>)</symbol>
        {self.compile_subroutine_body()}
      </subroutineDec>
    """


  def compile_parameter_list(self): # DONE
    parameter_list = "<parameterList>"

    while self.tokenizer.current_token != ')':
      parameter_list += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    parameter_list += "</parameterList>"

    return parameter_list


  def compile_subroutine_body(self): # DONE
    self.tokenizer.advance()
    self.assert_symbol('{')

    statements = self.compile_statements()

    # compile_statements() should have already advanced to "}" for us.
    self.assert_symbol('}')

    return f"""
      <subroutineBody>
        <symbol>{{</symbol>
        {statements}
        <symbol>}}</symbol>
      </subroutineBody>
    """


  def compile_var_dec(self): # DONE
    var_dec = "<varDec>"

    while self.tokenizer.symbol() != ';':
      var_dec += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    var_dec += "<symbol>;</symbol>"
    var_dec += "</varDec>"

    return var_dec


  def compile_statements(self):
    statements = "<statements>"

    self.tokenizer.advance()

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

    self.tokenizer.advance()
    self.assert_symbol(')')

    self.tokenizer.advance()
    self.assert_symbol('{')

    statements = self.compile_statements()

    self.assert_symbol('}')

    else_content = ""

    if self.tokenizer.peek() == 'else':
      self.tokenizer.advance()

      self.tokenizer.advance()
      self.assert_symbol('{')

      else_statements = self.compile_statements()

      self.assert_symbol('}')

      else_content = f"""
        <keyword>else</keyword>
        <symbol>{{</symbol>
        {else_statements}
        <symbol>}}</symbol>
      """

    return f"""
      <ifStatement>
        <keyword>if</keyword>
        <symbol>(</symbol>
        {expression}
        <symbol>)</symbol>
        <symbol>{{</symbol>
        {statements}
        <symbol>}}</symbol>
        {else_content}
      </ifStatement>
    """


  def compile_while_statement(self):
    pass


  def compile_let(self):
    self.tokenizer.advance()
    identifier = self.tokenizer.identifier()

    self.tokenizer.advance()
    self.assert_symbol('=')

    self.tokenizer.advance()
    expression = self.compile_expression()

    return f"""
      <letStatement>
        <keyword>let</keyword>
        <identifier>{identifier}</identifier>
        <symbol>=</symbol>
        {expression}
        <symbol>;</symbol>
      </letStatement>
    """


  def compile_if(self):
    pass


  def compile_while(self):
    pass


  def compile_do(self):
    pass


  # TODO: Handle expressions
  def compile_return(self):
    self.tokenizer.advance()
    self.assert_symbol(';')

    return f"""
      <returnStatement>
        <keyword>return</keyword>
        <symbol>;</symbol>
      </returnStatement>
    """


  def compile_expression(self):
    term = self.compile_term()

    return f"""
      <expression>
        {term}
      </expression>
    """


  def compile_term(self):
    token_type = self.tokenizer.token_type
    current_token = self.tokenizer.current_token

    return f"""
      <term>
        <{token_type}>{current_token}</{token_type}>
      </term>
    """


  def compile_expression_list(self):
    expression_list = "<expressionList>"

    while self.tokenizer.symbol() in (None, ','):
      if self.tokenizer.symbol() == ',':
        expression_list += "<symbol>,</symbol>"
      else:
        expression_list += self.compile_expression()

      self.tokenizer.advance()

    expression_list += "</expressionList>"


  def compile_statement(self):
    if self.tokenizer.current_token == 'class':
      return self.compile_class()

    if self.tokenizer.current_token in ['constructor', 'function', 'method']:
      return self.compile_subroutine_dec()

    if self.tokenizer.current_token == 'let':
      return self.compile_let()

    if self.tokenizer.current_token == 'if':
      return self.compile_if_statement()

    if self.tokenizer.current_token == 'var':
      return self.compile_var_dec()

    if self.tokenizer.current_token in ['static', 'field']:
      return self.compile_class_var_dec()

    if self.tokenizer.current_token == 'return':
      return self.compile_return()

    raise AssertionError(f"Unrecognized token in compile_statement(): {self.tokenizer.current_token}")


  def assert_symbol(self, symbol):
    assert self.tokenizer.symbol() == symbol, f"Expected {symbol} but found: " + self.tokenizer.current_token
