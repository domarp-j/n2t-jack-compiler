"""
SymbolTable

Given a field, static, var, or argument variable,
store the variable in a symbol table.

Create a new SymbolTable for each scope (class, subroutine).

There will only be at most two SymbolTables at a given time (class & subroutine).

"When compilng error-free Jack code, each symbol not found in the symbol tables can be assumed to be either a subroutine name or a class name."
"""


class SymbolTable:
  def __init__(self):
    self.table = {}
    self.reset_kind_count()


  # Start a new subroutine scope.
  # In other words, reset the SymbolTable.
  def start_subroutine(self):
    self.table = {}
    self.reset_kind_count()


  # Define a new identifier of the given name, type, and kind.
  # Assign a running index.
  def define(self, name, typ, kind):
    self.assert_valid_kind(kind)

    self.table[name] = {
      "type": typ,
      "kind": kind,
      "count": self.kind_count[kind]
    }

    self.kind_count[kind] += 1


  def var_count(self, kind):
    self.assert_valid_kind(kind)

    return self.kind_count[kind]


  def kind_of(self, name):
    return self.table[name]["kind"]


  def type_of(self, name):
    return self.table[name]["type"]


  def index_of(self, name):
    return self.table[name]["count"]


  def reset_kind_count(self):
    self.kind_count = {
      "field": 0,
      "static": 0,
      "argument": 0,
      "local": 0
    }


  def assert_valid_kind(self, kind):
    assert kind in self.kind_count.keys(), f"Invalid kind in SymbolTable.define(): {kind}"
