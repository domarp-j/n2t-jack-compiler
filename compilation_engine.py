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

    self.if_counter = 0
    self.while_counter = 0


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
    class_name = self.tokenizer.current_token

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
      self.compile_subroutine_dec(class_name)
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

    # do subroutine calls always return *something*.
    # We need to dump this return value immediately, since we'll never use it.
    self.vm_writer.write_pop('temp', 0)


  def compile_expression(self):
    self.compile_term()

    self.tokenizer.advance()

    if self.tokenizer.op():
      binary_op = self.tokenizer.current_token

      self.tokenizer.advance()
      self.compile_term()

      self.vm_writer.write_binary_op(binary_op)

      self.tokenizer.advance()


  def compile_expression_list(self):
    expression_count = 0

    while self.tokenizer.current_token not in [')', '}']:
      if self.tokenizer.current_token == ',':
        self.tokenizer.advance()
      else:
        expression_count += 1
        self.compile_expression()

    return expression_count


  def compile_if_statement(self):
    self.assert_keyword('if')

    # Increment if_counter for VM labeling.
    self.if_counter += 1

    label_1 = f"IF-STATEMENT-{self.if_counter}-A"
    label_2 = f"IF-STATEMENT-{self.if_counter}-B"

    self.tokenizer.advance()
    self.assert_symbol('(')

    # Write if-statement's expression to VM.
    self.tokenizer.advance()
    self.compile_expression()

    self.assert_symbol(')')

    # Write not and if-goto to label 1.
    self.vm_writer.write_command('not')
    self.vm_writer.write_if(label_1)

    self.tokenizer.advance()
    self.assert_symbol('{')

    # Write statements in if-block.
    self.tokenizer.advance()
    self.compile_statements()

    self.assert_symbol('}')

    # Write goto to label 2.
    self.vm_writer.write_goto(label_2)

    # Write label 1.
    self.vm_writer.write_label(label_1)

    if self.tokenizer.peek() == 'else':
      self.tokenizer.advance()

      self.tokenizer.advance()
      self.assert_symbol('{')

      # Write statements in else-block, if available.
      self.tokenizer.advance()
      self.compile_statements()

      self.assert_symbol('}')

    # Write label 2.
    self.vm_writer.write_label(label_2)


  def compile_let(self):
    self.assert_keyword('let')

    self.tokenizer.advance()
    self.assert_identifier()
    name = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_symbol()

    # TODO: Handle arrays
    # if self.tokenizer.current_token == '[':
    #   let_statement += self.add_xml_for_current_token()
    #   self.tokenizer.advance()
    #   let_statement += self.compile_expression()
    #   self.assert_symbol(']')
    #   let_statement += self.add_xml_for_current_token()
    #   self.tokenizer.advance()

    self.assert_symbol('=')

    self.tokenizer.advance()
    self.compile_expression()

    self.assert_symbol(';')

    self.vm_writer.write_pop(self.subroutine_symbol_table.kind_of(name), self.subroutine_symbol_table.index_of(name))


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
    else:
      self.vm_writer.write_push('constant', 0)

    self.vm_writer.write_return()

    self.assert_symbol(';')


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
    while self.tokenizer.current_token != '}':
      if self.tokenizer.symbol():
        pass
      else:
        self.compile_statement()

      self.tokenizer.advance()


  def compile_subroutine_body(self, class_name, subroutine_name):
    self.tokenizer.advance()
    self.assert_symbol('{')

    local_count = 0

    self.tokenizer.advance()

    while self.tokenizer.current_token == 'var':
      local_count += self.compile_var_dec()
      self.tokenizer.advance()

    self.vm_writer.write_function(f"{class_name}.{subroutine_name}", local_count)

    self.compile_statements()

    self.assert_symbol('}')


  def compile_subroutine_call(self):
    # Subroutine name OR class name
    self.assert_identifier()
    subroutine_name = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_symbol(['(', '.'])

    # If current token is period, this is a method call, e.g. obj.doThing()
    # If not, then its simply a function call, e.g. doAThing()
    if self.tokenizer.current_token == '.':
      subroutine_name += "."

      # Method name, e.g. doAThing in obj.doAThing()
      self.tokenizer.advance()
      self.assert_identifier()
      subroutine_name += self.tokenizer.current_token

      self.tokenizer.advance()

    self.assert_symbol('(')

    self.tokenizer.advance()
    arg_count = self.compile_expression_list()

    self.assert_symbol(')')

    self.vm_writer.write_call(subroutine_name, arg_count)


  def compile_subroutine_dec(self, class_name):
    self.assert_keyword(['constructor', 'method', 'function'])
    subroutine_type = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_return_type()
    return_type = self.tokenizer.current_token

    if subroutine_type == 'method':
      self.subroutine_symbol_table.define('this', return_type, 'argument')

    self.tokenizer.advance()
    self.assert_identifier()
    subroutine_name = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_symbol('(')

    self.tokenizer.advance()
    self.compile_parameter_list()

    # compile_parameter_list() should have already advanced to ")" for us.
    self.assert_symbol(')')

    self.compile_subroutine_body(class_name, subroutine_name)


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
      unary_op = self.tokenizer.current_token

      self.tokenizer.advance()
      self.compile_term()

      self.vm_writer.write_unary_op(unary_op)

    # Handle parentheses surrounding expressions.
    elif self.tokenizer.current_token == '(':
      self.tokenizer.advance()
      self.compile_expression()

      self.assert_symbol(')')

    # Handle integers
    elif self.tokenizer.int_val():
      self.vm_writer.write_push("constant", self.tokenizer.current_token)

    # Handling keywords
    elif self.tokenizer.keyword():
      if self.tokenizer.current_token in ["null", "false"]:
        self.vm_writer.write_push("constant", 0)
      elif self.tokenizer.current_token == "true":
        self.vm_writer.write_push("constant", 1)
        self.vm_writer.write_command("neg")
      else:
        raise AssertionError(f"Unrecognized keyword expression: {self.tokenizer.current_token}")

    # Handle identifiers that are not function calls x() or array accessors x[]
    elif self.tokenizer.identifier():
      name = self.tokenizer.current_token

      if self.subroutine_symbol_table.has_name(name):
        self.vm_writer.write_push(
          self.subroutine_symbol_table.kind_of(name),
          self.subroutine_symbol_table.index_of(name)
        )
      elif self.class_symbol_table.has_name(name):
        self.vm_writer.write_push(
          self.class_symbol_table.kind_of(name),
          self.class_symbol_table.index_of(name)
        )
      else:
        raise AssertionError(f"Unknown identifier: {name}")

    # Handle:
    # - strings
    # - keywords
    else:
      # TODO: Handle these
      pass


  def compile_var_dec(self):
    var_count = 1

    self.assert_keyword('var')
    kind = 'local'
    self.tokenizer.advance()

    typ = self.tokenizer.current_token
    self.tokenizer.advance()

    name = self.tokenizer.current_token
    self.tokenizer.advance()

    self.subroutine_symbol_table.define(name, typ, kind)

    # Handle comma-separated variable declarations.
    while self.tokenizer.current_token != ';':
      self.assert_symbol(',')
      var_count += 1
      self.tokenizer.advance()

      name = self.tokenizer.current_token
      self.tokenizer.advance()

      self.subroutine_symbol_table.define(name, typ, kind)

    return var_count


  def compile_while_statement(self):
    self.assert_keyword('while')

    # Increment while_counter for VM labeling.
    self.while_counter += 1

    label_1 = f"WHILE-STATEMENT-{self.while_counter}-A"
    label_2 = f"WHILE-STATEMENT-{self.while_counter}-B"

    # Write label 1.
    self.vm_writer.write_label(label_1)

    self.tokenizer.advance()
    self.assert_symbol('(')

    # Write the while's expression.
    self.tokenizer.advance()
    self.compile_expression()

    self.assert_symbol(')')

    # Write the not and if-goto statements.
    self.vm_writer.write_command("not")
    self.vm_writer.write_if(label_2)

    self.tokenizer.advance()
    self.assert_symbol('{')

    # Write the while's inner statements.
    self.tokenizer.advance()
    self.compile_statements()

    self.assert_symbol('}')

    # Write the goto statement.
    self.vm_writer.write_goto(label_1)

    # Write label 2.
    self.vm_writer.write_label(label_2)
