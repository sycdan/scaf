from example.test_timestamp_handling.command import TestTimestampHandling


def handle(command: TestTimestampHandling):
  assert isinstance(command.timestamp, str), (
    f"Expected timestamp to be a string due to lack of parsing logic, but got: {command.timestamp}"
  )
  return command.Result(type_name=type(command.timestamp).__name__, timestamp=command.timestamp)
