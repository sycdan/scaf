from example.test_timestamp_handling.command import TestTimestampHandling


def handle(command: TestTimestampHandling):
  return command.Result(type_name=type(command.timestamp).__name__, timestamp=command.timestamp)
