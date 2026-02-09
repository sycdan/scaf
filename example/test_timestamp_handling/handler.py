from example.test_timestamp_handling.command import TestTimestampHandling


def handle(command: TestTimestampHandling):
  return f"Received timestamp: {command.timestamp}"
