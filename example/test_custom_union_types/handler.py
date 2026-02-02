from example.test_custom_union_types.command import TestCustomUnionTypes


def handle(command: TestCustomUnionTypes):
  return type(command.entity).__name__
