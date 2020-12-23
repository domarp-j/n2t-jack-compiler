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


  def compile_class(self):
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


  def compile_class_var_dec(self):
    class_var_dec = "<classVarDec>"

    while self.tokenizer.symbol() != ';':
      class_var_dec += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    class_var_dec += "<symbol>;</symbol>"
    class_var_dec += "</classVarDec>"

    return class_var_dec


  def compile_subroutine_dec(self):
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
        <keyword>function</keyword>
        <keyword>{return_type}</keyword>
        <identifier>{identifier}</identifier>
        <symbol>(</symbol>
        {parameter_list}
        <symbol>)</symbol>
        {self.compile_subroutine_body()}
      </subroutineDec>
    """


  def compile_parameter_list(self):
    parameter_list = "<parameterList>"

    while self.tokenizer.current_token != ')':
      parameter_list += f"""
        <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
      """
      self.tokenizer.advance()

    parameter_list += "</parameterList>"

    return parameter_list


  def compile_subroutine_body(self):
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


  def compile_var_dec(self):
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
      statements += self.compile_statement()
      self.tokenizer.advance()

    statements += "<symbol>}</symbol>"
    statements += "</statements>"

    return statements


  def compile_if_statement(self):
    pass


  def compile_while_statement(self):
    pass


  def compile_let(self):
    self.tokenizer.advance()
    identifier = self.tokenizer.identifier

    self.tokenizer.advance()
    self.assert_symbol('=')

    expression = self.compile_expression()

    return f"""
      <letStatement>
        <keyword>let</keyword>
        <identifier>{identifier}</identifier>
        <symbol>=</identifier>
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
    # term = self.compile_term()

    # return f"""
    #   <expression>
    #     {term}
    #   </expression>
    # """
    pass


  def compile_term(self):
    # self.tokenizer.advance()

    # return f"""
    #   <term>
    #     <{self.tokenizer.token_type}>{self.tokenizer.current_token}</{self.tokenizer.token_type}>
    #   </term>
    # """
    pass


  def compile_expression_list(self):
    # expression_list = "<expressionList>"

    # while self.tokenizer.symbol() != ',':
    #   pass

    # expression_list += "</expressionList>"
    pass


  def compile_statement(self):
    if self.tokenizer.current_token == 'class':
      return self.compile_class()

    if self.tokenizer.current_token == 'function':
      return self.compile_subroutine_dec()

    if self.tokenizer.current_token == 'let':
      return self.compile_let()

    if self.tokenizer.current_token == 'var':
      return self.compile_var_dec()

    if self.tokenizer.current_token in ['static', 'field']:
      return self.compile_class_var_dec()

    if self.tokenizer.current_token == 'return':
      return self.compile_return()

    raise AssertionError(f"Unrecognized token in compile_statement(): {self.tokenizer.current_token}")


  def assert_symbol(self, symbol):
    assert self.tokenizer.symbol() == symbol, f"Expected {symbol} but found: " + self.tokenizer.current_token
