from example.custom_union_types.command import TestCustomUnionTypes


def handle(command: TestCustomUnionTypes):
  return command.Result(type_name=type(command.entity).__name__, entity=command.entity)
