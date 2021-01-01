"""
CompilationEngine
"""


from symbol_table import SymbolTable


class CompilationEngine:
  def __init__(self, tokenizer, vm_writer):
    # We will use the passed-in JackTokenizer to parse the given Jack code.
    self.tokenizer = tokenizer

    # We will use the passed-in VMWriter to write our compiled VM code.
    # The VMWriter instance should have already create the .vm file for us.
    self.vm_writer = vm_writer

    # When handling Jack variable declarations, you need two symbol tables:
    # - a SymbolTable for the class scope, and
    # - a SymbolTable for the subroutine scope.
    self.class_symbol_table = SymbolTable()
    self.subroutine_symbol_table = SymbolTable()

    # Even though a class can contain multiple different subroutines,
    # we only ever need one subroutine symbol table.
    #
    # We can simply reset the subroutine symbol table
    # every time we encounter a new subroutine!

    # We will use simple counters to create distinct labels
    # for each if/while statement in the compiled VM code.
    self.if_counter = 0
    self.while_counter = 0

    # We'll need to track a subroutine's type as we parse it.
    # Its value is always one of ["function", "method", "constructor"].
    self.subroutine_type = None


  def run(self):
    # Advance to the first token in the .jack file.
    # This should always be "class".
    self.tokenizer.advance()

    # Let's get started!
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

    # Advance to the next token, which should be the class name.
    self.tokenizer.advance()
    self.assert_identifier()
    class_name = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_symbol('{')

    # We reset the class-level symbol table on the off-chance that
    # there are multiple classes defined in a .jack file.
    self.class_symbol_table.reset()

    # At this point, we may encounter class-level field or static variables.
    # We will compile those as needed.
    self.tokenizer.advance()
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['field', 'static']:
      self.compile_class_var_dec()
      self.tokenizer.advance()

    # We will compile each class's subroutines one at a time.
    while self.tokenizer.keyword() and self.tokenizer.current_token in ['constructor', 'function', 'method']:
      # We can safely reset the subroutine-level symbol table for each new subroutine.
      # There's no need to keep the old table.
      self.subroutine_symbol_table.reset()

      self.compile_subroutine_dec(class_name)
      self.tokenizer.advance()

    self.assert_symbol('}')


  def compile_class_var_dec(self):
    # We will store the variable kind, which should always be one of ['field', 'static'].
    self.assert_keyword(['field', 'static'])
    kind = self.tokenizer.current_token
    self.tokenizer.advance()

    # We'll also keep track of the variable's type.
    typ = self.tokenizer.current_token
    self.tokenizer.advance()

    # We'll need the variable's name, of course, to populate the symbol table.
    name = self.tokenizer.current_token
    self.tokenizer.advance()

    # We now have everything we need to update the class-level symbol table,
    # so let's do that!
    self.class_symbol_table.define(name, typ, kind)

    # It's completely possible that the programmer used comma-separated variable decs.
    # Example: field int x, y, z;
    # We will anticipate this and populate the symbol table accordingly.
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

    if self.subroutine_symbol_table.has_name(name):
      self.vm_writer.write_pop(
        self.subroutine_symbol_table.kind_of(name),
        self.subroutine_symbol_table.index_of(name)
      )
    elif self.class_symbol_table.has_name(name):
      kind = self.class_symbol_table.kind_of(name)
      kind = "this" if kind == "field" else kind

      self.vm_writer.write_pop(kind, self.class_symbol_table.index_of(name))
    else:
      raise AssertionError(f"Undeclared variable found: {name}")


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

    if self.tokenizer.keyword() and self.tokenizer.current_token == "this":
      self.vm_writer.write_push('pointer', 0)
      self.tokenizer.advance()
    elif self.tokenizer.current_token != ';':
      self.compile_expression()
    else:
      self.vm_writer.write_push('constant', 0)

    self.assert_symbol(';')

    self.vm_writer.write_return()


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
    # First, we'll do a sanity check and look for a left brace.
    # A left brace symbol indicates the start of a block of statements.
    self.tokenizer.advance()
    self.assert_symbol('{')

    # A function declaration in VM code has the format:
    # function MyClass.method local_count
    # We need to know the number of local variables in the function.
    # Let's initialize the local count.
    local_count = 0

    self.tokenizer.advance()

    # We'll now check for any local variable declarations.
    #
    # We'll compile each declaration we find and update the running tally
    # of our local count.
    while self.tokenizer.current_token == 'var':
      local_count += self.compile_var_dec()
      self.tokenizer.advance()

    # With the class name, subroutine name, and local count on hand,
    # we can finally declare our function in VM bytecode.
    self.vm_writer.write_function(f"{class_name}.{subroutine_name}", local_count)

    # Edge case!
    if self.subroutine_type == 'constructor':
      # If we're compiling a constructor, we'll need to do some initialization
      # before compiling any statements.

      # First, we'll use Memory.alloc() to allocate memory for the new object.
      field_count = self.class_symbol_table.var_count('field')
      self.vm_writer.write_push("constant", field_count)
      self.vm_writer.write_call("Memory.alloc", 1)

      # We will then anchor _this_ to the THIS base address.
      self.vm_writer.write_pop("pointer", 0)

    # Another edge case!
    elif self.subroutine_type == "method":
      # Since we're in a method, we need to initialize _this_ to the current object.
      # We can use our recently-updated symbol table to do this.
      # First, let's push the first argument _this_ onto the stack.
      self.vm_writer.write_push("argument", 0)

      # Next, we must immediately pop this value from the stack
      # and store it at the THIS address in memory.
      self.vm_writer.write_pop("pointer", 0)

      # Now the compiled code can access the object's fields.

    # We'll now compile every statement inside of the subroutine.
    self.compile_statements()

    # Finally, we'll do another sanity check to ensure we've hit the
    # end of our statement block.
    self.assert_symbol('}')


  def compile_subroutine_call(self):
    # We'll keep a running tally of the argument count.
    # This is required for the call VM code.
    # Example: call {subroutine_name} {arg_count}
    arg_count = 0

    # First, let's make sure that the current token is an identifier.
    self.assert_identifier()

    # This identifier can be one of the following:
    # - a subroutine name, such as doAThing in doAThing()
    # - a class name, such as MyClass in MyClass.doAThing()
    # - an object, such as myObj in myObj.doAThing()
    #
    # We'll store it for future use.
    name = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_symbol(['(', '.'])

    # If the current token is a '.', this is a method call.
    #
    # At this point in time, the name is either a class name or an object,
    # like MyClass or myObj.
    if self.tokenizer.current_token == '.':
      obj_in_sub_symbol_table = self.subroutine_symbol_table.has_name(name)
      obj_in_class_symbol_table = self.class_symbol_table.has_name(name)

      # If the current token is an object, we need to do something special.
      # Specifically, we need to push the current object onto the stack.
      #
      # In a sense, we're converting our object-oriented Jack code into
      # procedural code.
      #
      # myObj.doAThing(a, b) -> doAThing(myObj, a, b)
      #
      # From a VM perspective, the procedural version is easier to compile.
      if obj_in_sub_symbol_table or obj_in_class_symbol_table:
        arg_count += 1

        # First, we'll for the object identifier in the subroutine symbol table.
        if obj_in_sub_symbol_table:
          # Push the object to the stack.
          self.vm_writer.write_push(
            self.subroutine_symbol_table.kind_of(name),
            self.subroutine_symbol_table.index_of(name)
          )

          # We'll need to replace our current name with the object's type (aka class).
          name = self.subroutine_symbol_table.type_of(name)

        # Next, we'll check for the object identifier in the class symbol table.
        elif obj_in_class_symbol_table:
          kind = self.class_symbol_table.kind_of(name)
          kind = "this" if kind == "field" else kind

          # Push the object to the stack.
          self.vm_writer.write_push(
            kind,
            self.class_symbol_table.index_of(name)
          )

          # We'll need to replace our current name with the object's type (aka class).
          name = self.class_symbol_table.type_of(name)

      name += "."

      # At this point, we can be confident that we're at the method name.
      self.tokenizer.advance()
      self.assert_identifier()
      name += self.tokenizer.current_token

      self.tokenizer.advance()

    self.assert_symbol('(')

    # We'll need to compile every expression inside of the subroutine call.
    #
    # We'll also get the number of expressions in the call,
    # which will increase our argument counter.
    #
    # Example: myObj.doAThing(exp1, exp2, exp3...)
    self.tokenizer.advance()
    arg_count += self.compile_expression_list()

    self.assert_symbol(')')

    # FINALLY, we can write our VM code!
    self.vm_writer.write_call(name, arg_count)


  def compile_subroutine_dec(self, class_name):
    self.assert_keyword(['constructor', 'method', 'function'])
    self.subroutine_type = self.tokenizer.current_token

    self.tokenizer.advance()
    self.assert_return_type()
    return_type = self.tokenizer.current_token

    # Update subroutine symbol table with object reference, aka this.
    if self.subroutine_type == 'method':
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
    # We need to compile each individual term to VM code as needed.
    #
    # The definition for "term" in this context is quite broad,
    # so bear with me as we go through each possible term!

    # First, if we have an identifier on our hands, we'll need to peek one token ahead.
    #
    # The token ahead could be one of the following:
    # - a period, indicating that the identifier is a class name or object
    # - a left parens, indicating that the identifier is a subroutine
    # - a left bracket, indiciating that the identifier is an array
    if self.tokenizer.identifier() and self.tokenizer.peek() in ['.', '(', '[']:
      next_token = self.tokenizer.peek()

      # The next token is either a period or left parens,
      # which means we're in a subroutine call!
      #
      # Examples: Memory.alloc(), myObj.doAThing(), doSomethingElse()
      if next_token in ['.', '(']:
        self.compile_subroutine_call()

      # The next token is a left bracket, which means
      # we're trying to access an array.
      #
      # Examples: myArray[3], myArray[x + (y - 2)]
      elif next_token == '[':
        # TODO: Handle identifier.

        self.tokenizer.advance()
        self.assert_symbol('[')

        self.tokenizer.advance()
        self.compile_expression()

        self.assert_symbol(']')

    # Let's check if the current token is a unary operation,
    # such as "-" (negate, or neg) or "~" (not).
    #
    # Examples: -3, ~(~(x))
    elif self.tokenizer.unary_op():
      unary_op = self.tokenizer.current_token

      self.tokenizer.advance()
      self.compile_term()

      self.vm_writer.write_unary_op(unary_op)

    # We can always have expressions inside of parentheses.
    # We can treat this like its own term.
    # Examples: (x + 3), ((x + 2) > 9)
    elif self.tokenizer.current_token == '(':
      self.tokenizer.advance()
      self.compile_expression()

      self.assert_symbol(')')

    # Now we've reached some simpler terms!
    # If we encounter a number, we simply write "push constant {number}".
    elif self.tokenizer.int_val():
      self.vm_writer.write_push("constant", self.tokenizer.current_token)

    # We need to consider some special keywords.
    # Most of keywords ultimately resolve to simple "push constant" VM commands.
    # However, we want
    elif self.tokenizer.keyword():
      if self.tokenizer.current_token in ["null", "false"]:
        self.vm_writer.write_push("constant", 0)
      elif self.tokenizer.current_token == "true":
        self.vm_writer.write_push("constant", 1)
        self.vm_writer.write_command("neg")

    # If we have an identifer at this point, we can safely assume that
    # its a standalone variable, not part of a subroutine call or array access.
    #
    # We will leverage our symbol tables to write the VM code here.
    elif self.tokenizer.identifier():
      name = self.tokenizer.current_token

      # First, let's check the subroutine symbol table for the identifier.
      if self.subroutine_symbol_table.has_name(name):
        # If we find it, we can now write the VM push code.
        self.vm_writer.write_push(
          self.subroutine_symbol_table.kind_of(name),
          self.subroutine_symbol_table.index_of(name)
        )

      # Next, we'll check the class symbol table for the identifier.
      elif self.class_symbol_table.has_name(name):
        # We need to make a small tweak to address _field_s.
        kind = self.class_symbol_table.kind_of(name)
        kind = "this" if kind == "field" else kind

        # We can now write the VM push code.
        self.vm_writer.write_push(
          kind,
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
