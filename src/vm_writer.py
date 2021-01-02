"""
VMWriter

Emit VM Code to output .vm file.
"""

class VMWriter:
  def __init__(self, jack_file):
    vm_file = jack_file.replace(".jack", ".vm")

    self.vm_file = open(vm_file, "w")


  def write(self, line):
    self.vm_file.write(f"{line}\n")


  def close(self):
    self.vm_file.close()


  def write_push(self, segment, index):
    assert segment in [
      "constant",
      "argument",
      "local",
      "static",
      "this",
      "that",
      "pointer",
      "temp"
    ], f"Invalid push segment: {segment}"

    self.write(f"push {segment} {index}")


  def write_pop(self, segment, index):
    assert segment in [
      "argument",
      "local",
      "static",
      "this",
      "that",
      "pointer",
      "temp"
    ], f"Invalid pop segment: {segment}"

    self.write(f"pop {segment} {index}")


  def write_binary_op(self, op):
    if op == '+':
      self.write_command('add')
    elif op == '-':
      self.write_command('sub')
    elif op == '*':
      self.write_call('Math.multiply', 2)
    elif op == '/':
      self.write_call('Math.divide', 2)
    elif op == '=':
      self.write_command('eq')
    elif op == '>':
      self.write_command('gt')
    elif op == '<':
      self.write_command('lt')
    elif op == '&':
      self.write_command('and')
    elif op == '|':
      self.write_command('or')
    else:
      raise AssertionError(f"Unrecognized binary op: {op}")


  def write_unary_op(self, op):
    if op == '-':
      self.write_command('neg')
    elif op == '~':
      self.write_command('not')
    else:
      raise AssertionError(f"Unrecognized unary op: {op}")


  def write_command(self, command):
    assert command in [
      "add",
      "sub",
      "neg",
      "eq",
      "gt",
      "lt",
      "and",
      "or",
      "not"
    ], f"Invalid arithmetic command: {command}"

    self.write(command)


  def write_label(self, label):
    self.write(f"label {label}")


  def write_goto(self, label):
    self.write(f"goto {label}")


  def write_if(self, label):
    self.write(f"if-goto {label}")


  def write_call(self, name, arg_count):
    self.write(f"call {name} {arg_count}")


  def write_function(self, name, local_count):
    self.write(f"function {name} {local_count}")


  def write_return(self):
    self.write("return")
