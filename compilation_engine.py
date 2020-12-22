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
  def __init__(self, input_file, output_file):
    pass


  def compile_class(self):
    pass


  def compile_class_var_dec(self):
   pass


  def compile_subroutine_dec(self):
    pass


  def compile_parameter_list(self):
    pass


  def compile_subroutine_body(self):
    pass


  def compile_var_dec(self):
    pass


  def compile_statements(self):
    pass


  def compile_if_statement(self):
    pass


  def compile_while_statement(self):
    pass


  def compile_let(self):
    pass


  def compile_if(self):
    pass


  def compile_while(self):
    pass


  def compile_do(self):
    pass

  def compile_return(self):
    pass


  def compile_expression(self):
    pass


  def compile_term(self):
    pass


  def compile_expression_list(self):
    pass


